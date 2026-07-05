"""
Document Summarization Service.

Fast local summarization with document-specific handling. Resumes get a
structured brief; other documents use a small extractive summary.
"""

from __future__ import annotations

import re
from collections import Counter


_NUM_SENTENCES = 5
_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "that", "this", "it", "its", "as", "not",
    "also", "which", "their", "they", "he", "she", "we", "you", "i",
}

_SECTION_ALIASES = {
    "summary": "Summary",
    "professional summary": "Summary",
    "profile": "Summary",
    "education": "Education",
    "work experience": "Work Experience",
    "experience": "Work Experience",
    "employment": "Work Experience",
    "technical skills": "Technical Skills",
    "skills": "Technical Skills",
    "projects": "Projects",
}

_NOISE_CHARS = {
    "\u0083": "",
    "\u00d1": "",
    "\u00ef": "",
    "\uf0b7": "-",
}


class SummaryService:
    def clean_text(self, text: str) -> str:
        cleaned = text or ""

        for bad, replacement in _NOISE_CHARS.items():
            cleaned = cleaned.replace(bad, replacement)

        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = re.sub(r"(?m)^\s*[#|]\s*", "", cleaned)
        cleaned = re.sub(r"(?m)^\s*[-*]\s*", "- ", cleaned)

        return cleaned.strip()

    def summarize(self, text: str) -> str:
        cleaned = self.clean_text(text)
        if not cleaned:
            return ""

        if self._looks_like_resume(cleaned):
            return self._summarize_resume(cleaned)

        return self._summarize_extractively(cleaned)

    def _looks_like_resume(self, text: str) -> bool:
        lowered = text.lower()
        markers = [
            "work experience",
            "technical skills",
            "education",
            "projects",
            "relevant coursework",
            "data engineer",
            "data analyst",
        ]
        return sum(marker in lowered for marker in markers) >= 2

    def _summarize_resume(self, text: str) -> str:
        sections = self._split_sections(text)
        output: list[str] = []

        name = self._first_nonempty_line(text)
        if name:
            output.extend(["Candidate Snapshot", f"- {name}"])

        summary = self._compact_section(sections.get("Summary", ""), 2)
        if summary:
            output.extend(["", "Overview", *summary])

        experience = self._extract_experience(sections.get("Work Experience", ""))
        if experience:
            output.extend(["", "Experience Highlights", *experience[:4]])

        skills = self._extract_skills(sections.get("Technical Skills", ""))
        if skills:
            output.extend(["", "Core Skills", *skills[:5]])

        projects = self._compact_section(sections.get("Projects", ""), 3)
        if projects:
            output.extend(["", "Projects", *projects])

        education = self._compact_section(sections.get("Education", ""), 2)
        if education:
            output.extend(["", "Education", *education])

        if len(output) <= 2:
            return self._summarize_extractively(text)

        return "\n".join(output)

    def _split_sections(self, text: str) -> dict[str, str]:
        sections: dict[str, list[str]] = {}
        current = "Header"

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            key = re.sub(r"[^a-z ]", "", line.lower()).strip()
            section = _SECTION_ALIASES.get(key)

            if section:
                current = section
                sections.setdefault(current, [])
                continue

            sections.setdefault(current, []).append(line)

        return {
            name: "\n".join(lines).strip()
            for name, lines in sections.items()
            if lines
        }

    def _extract_experience(self, text: str) -> list[str]:
        if not text:
            return []

        lines = [line for line in text.splitlines() if line.strip()]
        highlights: list[str] = []
        current_company = ""
        current_role = ""

        for line in lines:
            if line.startswith("-"):
                if current_role and len(highlights) < 4:
                    highlights.append(f"- {current_role}: {line.lstrip('- ').strip()}")
                continue

            if re.search(r"\b(20\d{2}|19\d{2}|present|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", line, re.I):
                continue

            if len(line) < 45 and not current_company:
                current_company = line
                continue

            if len(line) < 70 and current_company:
                current_role = f"{current_company} - {line}"
                current_company = ""

        return highlights

    def _extract_skills(self, text: str) -> list[str]:
        skills: list[str] = []

        for line in text.splitlines():
            clean = line.strip()
            if not clean:
                continue

            if ":" in clean:
                label, values = clean.split(":", 1)
                values = values.strip().rstrip(".")
                if values:
                    skills.append(f"- {label.strip()}: {values}")
            else:
                skills.append(f"- {clean.rstrip('.')}")

        return skills

    def _compact_section(self, text: str, limit: int) -> list[str]:
        if not text:
            return []

        lines = []
        for line in text.splitlines():
            clean = line.strip().rstrip(".")
            if not clean:
                continue
            if clean.startswith("-"):
                clean = clean.lstrip("- ").strip()
            lines.append(f"- {clean}")
            if len(lines) >= limit:
                break

        return lines

    def _summarize_extractively(self, text: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        if len(sentences) <= _NUM_SENTENCES:
            return text.strip()

        words = re.findall(r"\b[a-z]{2,}\b", text.lower())
        freq = Counter(w for w in words if w not in _STOPWORDS)

        scores = []
        for sent in sentences:
            tokens = re.findall(r"\b[a-z]{2,}\b", sent.lower())
            score = sum(freq[t] for t in tokens if t not in _STOPWORDS)
            scores.append(score / (len(tokens) + 1))

        top_idx = sorted(
            range(len(sentences)),
            key=lambda i: scores[i],
            reverse=True,
        )[:_NUM_SENTENCES]
        top_idx.sort()

        return " ".join(sentences[i] for i in top_idx)

    def _first_nonempty_line(self, text: str) -> str:
        for line in text.splitlines():
            clean = line.strip()
            if clean:
                return clean
        return ""
