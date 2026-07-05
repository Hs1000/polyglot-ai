"""
Chat Service — semantic retrieval + extractive QA.

Pipeline:
  1. Split the document into overlapping ~200-word chunks.
  2. Embed each chunk with sentence-transformers/all-MiniLM-L6-v2 (80 MB).
  3. Embed the user question with the same model.
  4. Cosine-similarity rank → keep top-k chunks.
  5. Run deepset/roberta-base-squad2 extractive QA over the retrieved chunks.

Semantic retrieval fixes vocabulary mismatches like "programming languages"
vs "Languages and Databases: Python, Java…" — the embedding model knows
they mean the same thing even though the tokens differ.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)

_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_QA_MODEL    = "deepset/roberta-base-squad2"

_CHUNK_WORDS   = 200   # words per chunk
_CHUNK_OVERLAP = 100   # overlap — large enough so section headers appear near chunk starts
_TOP_K         = 3     # number of chunks to pass to the QA model
_MAX_WORDS     = 15_000  # hard cap before chunking

_SCORE_LOW = 0.002  # below this QA confidence → "not found" fallback


_shared_instance: "ChatService | None" = None


def get_chat_service() -> "ChatService":
    """Return the process-wide ChatService singleton."""
    global _shared_instance
    if _shared_instance is None:
        _shared_instance = ChatService()
    return _shared_instance


class ChatService:

    def __init__(self):
        self._embed_model = None
        self._qa_pipeline = None

    # ── model loaders ─────────────────────────────────────────────────────────

    def _get_embed_model(self):
        if self._embed_model is None:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model: %s…", _EMBED_MODEL)
            self._embed_model = SentenceTransformer(_EMBED_MODEL)
            logger.info("Embedding model ready.")
        return self._embed_model

    def _get_qa_pipeline(self):
        if self._qa_pipeline is None:
            from transformers import pipeline
            logger.info("Loading QA model: %s…", _QA_MODEL)
            self._qa_pipeline = pipeline("question-answering", model=_QA_MODEL)
            logger.info("QA model ready.")
        return self._qa_pipeline

    # ── public API ────────────────────────────────────────────────────────────

    def ask(self, document_text: str, question: str) -> str:
        words = document_text.split()
        if len(words) > _MAX_WORDS:
            document_text = " ".join(words[:_MAX_WORDS])

        chunks = self._chunk(document_text)

        # Retrieve top-K chunks by semantic similarity
        top_chunks, best_retrieval_score = self._retrieve_top_k(question, chunks)

        # Run QA on each candidate chunk separately; keep the best-scoring answer.
        # Running separately (not joined) preserves high per-chunk QA confidence.
        qa_pipe = self._get_qa_pipeline()
        best_answer, best_qa_score, best_chunk = "", 0.0, ""
        for chunk in top_chunks:
            result = qa_pipe(
                question=question,
                context=chunk,
                max_answer_len=60,
                doc_stride=128,
            )
            if result["score"] > best_qa_score:
                best_qa_score = result["score"]
                best_answer   = result["answer"].strip()
                best_chunk    = chunk

        # If the answer ends with a comma the model stopped mid-list.
        # Extend to the next newline so the full comma-separated value is returned.
        if best_answer.endswith(",") and best_chunk:
            best_answer = self._extend_list(best_answer, best_chunk)

        # Adaptive threshold: relax the floor when retrieval is semantically
        # confident so vocabulary-mismatch answers still come through.
        retrieval_confident = best_retrieval_score > 0.25
        effective_low = 0.001 if retrieval_confident else _SCORE_LOW

        if not best_answer or best_qa_score < effective_low:
            return (
                "I couldn't find a clear answer to that in the document. "
                "Try rephrasing or ask about something specific mentioned in the text."
            )

        return best_answer

    # ── internals ─────────────────────────────────────────────────────────────

    def _extend_list(self, answer: str, context: str) -> str:
        """Extend a truncated comma-separated answer to the end of its list.

        Stops at the next section label (e.g. 'Technologies:') or newline so
        we don't bleed into adjacent sections.
        """
        import re
        pos = context.find(answer)
        if pos == -1:
            return answer
        tail = context[pos + len(answer):]
        # A new section label looks like " Word:" or " Word/Word:"
        section = re.search(r'\s+[A-Z][A-Za-z/]+:', tail)
        newline  = tail.find("\n")
        stops = []
        if section:
            stops.append(section.start())
        if newline != -1:
            stops.append(newline)
        if not stops:
            period = tail.find(".")
            if period != -1:
                stops.append(period)
        if not stops:
            return answer
        cut = pos + len(answer) + min(stops)
        return context[pos:cut].strip()

    def _chunk(self, text: str) -> list[str]:
        """Split text into overlapping word-based chunks."""
        words = text.split()
        chunks, i = [], 0
        while i < len(words):
            chunk = " ".join(words[i : i + _CHUNK_WORDS])
            chunks.append(chunk)
            i += _CHUNK_WORDS - _CHUNK_OVERLAP
        return chunks or [text]

    def _retrieve_top_k(self, question: str, chunks: list[str]) -> tuple[list[str], float]:
        """Return (top-K chunks by cosine similarity, best similarity score).

        We run QA on each chunk individually rather than joining them — joining
        dilutes confidence scores. Returning multiple candidates handles cases
        where the retrieval model mis-ranks due to vocabulary mismatch.
        """
        if len(chunks) <= _TOP_K:
            return chunks, 1.0

        model = self._get_embed_model()
        q_vec      = model.encode(question, normalize_embeddings=True)
        chunk_vecs = model.encode(chunks,   normalize_embeddings=True, batch_size=32)

        scores   = chunk_vecs @ q_vec
        top_idxs = list(np.argsort(scores)[::-1][:_TOP_K])

        # Always include the first chunk — names, titles, and dates are almost
        # always in the document header, which retrieval may under-rank.
        if 0 not in top_idxs:
            top_idxs.append(0)

        top_chunks = [chunks[i] for i in top_idxs]
        best_score = float(scores[top_idxs[0]])

        return top_chunks, best_score
