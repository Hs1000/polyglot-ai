import logging

logger = logging.getLogger(__name__)

# Field schemas: label → question sent to the QA pipeline
_SCHEMAS: dict[str, dict[str, str]] = {
    "resume": {
        "Name":                 "What is the candidate's full name?",
        "Email":                "What is the email address?",
        "Phone":                "What is the phone number?",
        "Degree":               "What is the candidate's highest degree?",
        "University":           "Which university did the candidate attend most recently?",
        "Graduation Date":      "When did the candidate graduate?",
        "GPA":                  "What is the candidate's GPA?",
        "Programming Languages":"What programming languages does the candidate know?",
        "Frameworks":           "What libraries or frameworks does the candidate use?",
        "Databases & Tools":    None,  # scanned directly from text — QA is unreliable for proper nouns
        "Recent Job Title":     None,  # parsed directly from Work Experience section
        "Recent Employer":      None,  # parsed directly from Work Experience section
        "Years of Experience":  None,  # calculated from date ranges in Work Experience
    },
    "invoice": {
        "Vendor":          "Who is the vendor or supplier?",
        "Invoice Number":  "What is the invoice number?",
        "Invoice Date":    "What is the invoice date?",
        "Due Date":        "What is the payment due date?",
        "Total Amount":    "What is the total amount due?",
        "Payment Terms":   "What are the payment terms?",
        "Bill To":         "Who is the invoice billed to?",
    },
    "contract": {
        "Parties":          "Who are the parties involved in this contract?",
        "Effective Date":   "What is the effective date of the contract?",
        "Expiration Date":  "When does the contract expire or terminate?",
        "Governing Law":    "What is the governing law or jurisdiction?",
        "Payment Terms":    "What are the payment terms?",
        "Notice Period":    "What is the notice period for termination?",
    },
    "research": {
        "Title":        "What is the title of the paper or research?",
        "Authors":      "Who are the authors?",
        "Abstract":     "What is the abstract or summary of the paper?",
        "Methodology":  "What methodology or approach was used?",
        "Dataset":      "What dataset was used?",
        "Results":      "What are the main results or findings?",
        "Conclusion":   "What is the conclusion?",
    },
    "report": {
        "Title":        "What is the title of the report?",
        "Author":       "Who authored or prepared the report?",
        "Date":         "What is the report date?",
        "Summary":      "What is the executive summary or overview?",
        "Key Findings": "What are the key findings or recommendations?",
        "Period":       "What time period does the report cover?",
    },
    "general": {
        "Title / Subject": "What is the title or subject of this document?",
        "Author":          "Who is the author?",
        "Date":            "What is the date of this document?",
        "Main Topic":      "What is this document mainly about?",
        "Key Points":      "What are the key points or conclusions?",
    },
}

# Keywords used to detect document type
_TYPE_SIGNALS: dict[str, list[str]] = {
    "resume":   ["work experience", "education", "resume", "curriculum vitae", "gpa",
                 "bachelor", "master", "internship", "skills", "objective", "summary"],
    "invoice":  ["invoice", "invoice number", "amount due", "bill to", "subtotal",
                 "tax", "payment due", "purchase order"],
    "contract": ["agreement", "contract", "terms and conditions", "governing law",
                 "whereas", "party", "parties", "clause", "herein", "termination"],
    "research": ["abstract", "methodology", "references", "introduction", "related work",
                 "conclusion", "arxiv", "journal", "proceedings", "doi"],
    "report":   ["executive summary", "quarterly", "annual report", "fiscal year",
                 "revenue", "earnings", "forecast", "recommendations"],
}


class ExtractionService:

    def _get_chat_service(self):
        from app.services.chat_service import get_chat_service
        return get_chat_service()

    def extract(self, document_text: str) -> dict:
        from app.services.tech_vocab import (
            KNOWN_DATABASES, KNOWN_FRAMEWORKS, KNOWN_LANGUAGES,
            scan_for_known, tokenise,
        )

        doc_type = self._detect_type(document_text)
        schema = _SCHEMAS[doc_type]
        svc = self._get_chat_service()

        # Pre-parse work experience for resume so QA doesn't mis-attribute
        recent_employer, recent_title, years_of_exp = None, None, None
        if doc_type == "resume":
            recent_employer, recent_title = self._parse_recent_work(document_text)
            years_of_exp = self._calculate_experience(document_text)

        fields: dict[str, str | None] = {}
        for label, question in schema.items():
            try:
                if label == "Recent Employer":
                    fields[label] = recent_employer
                    continue
                if label == "Recent Job Title":
                    fields[label] = recent_title
                    continue
                if label == "Years of Experience":
                    fields[label] = years_of_exp
                    continue
                if label == "Databases & Tools":
                    # QA is unreliable for proper-noun database names; scan directly.
                    found = scan_for_known(document_text, KNOWN_DATABASES)
                    fields[label] = ", ".join(found) if found else None
                    continue
                if question is None:
                    fields[label] = None
                    continue

                answer = svc.ask(document_text, question)
                if "couldn't find" in answer.lower():
                    fields[label] = None
                else:
                    cleaned = self._clean(label, answer)
                    # Filter tech fields through known sets so QA bleed-over
                    # (e.g. "Neo4J" appearing in a Languages answer) is removed.
                    if label == "Programming Languages":
                        kept = [t for t in tokenise(cleaned) if t in KNOWN_LANGUAGES]
                        fields[label] = ", ".join(kept) if kept else None
                    elif label == "Frameworks":
                        kept = [t for t in tokenise(cleaned) if t in KNOWN_FRAMEWORKS]
                        fields[label] = ", ".join(kept) if kept else None
                    else:
                        fields[label] = cleaned
            except Exception:
                logger.exception("Extraction failed for field %r", label)
                fields[label] = None

        return {"document_type": doc_type, "fields": fields}

    # Common section heading variants across different resume styles
    _WORK_SECTION_NAMES = [
        "Work Experience", "Professional Experience", "Experience",
        "Work History", "Employment History", "Career History",
        "Employment", "Professional Background",
    ]

    # Section headings that mark the END of the work experience block
    _NEXT_SECTION_NAMES = [
        "Education", "Skills", "Technical Skills", "Projects",
        "Certifications", "Awards", "Publications", "Volunteer",
        "Interests", "References",
    ]

    _MONTH_MAP = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }

    def _find_work_section(self, text: str):
        """Return a regex match for the work experience heading, trying all variants."""
        import re
        pattern = r'(?:' + '|'.join(re.escape(n) for n in self._WORK_SECTION_NAMES) + r')\s*\n'
        return re.search(pattern, text, re.IGNORECASE)

    def _work_section_text(self, text: str) -> str | None:
        """Return just the text of the work experience section."""
        import re
        m = self._find_work_section(text)
        if not m:
            return None
        section = text[m.end():]
        end_pattern = r'\n(?:' + '|'.join(re.escape(n) for n in self._NEXT_SECTION_NAMES) + r')\s*\n'
        end = re.search(end_pattern, section, re.IGNORECASE)
        return section[:end.start()] if end else section

    def _parse_recent_work(self, text: str) -> tuple[str | None, str | None]:
        """Extract company and job title from the first work experience entry."""
        import re
        section = self._work_section_text(text)
        if not section:
            return None, None

        lines       = [l.strip() for l in section.splitlines() if l.strip()]
        date_re     = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}', re.IGNORECASE)
        location_re = re.compile(r'.+,\s*[A-Z]{2}(?:\s|$)')
        bullet_re   = re.compile(r'^[•\-\*]')

        company, title = None, None
        for line in lines[:12]:
            if date_re.search(line) or bullet_re.match(line):
                break
            if location_re.match(line):
                continue
            if company is None:
                company = line
            elif title is None:
                title = line
                break

        return company, title

    def _calculate_experience(self, text: str) -> str | None:
        """Sum all date ranges in the work experience section and return a human-readable duration."""
        import re
        from datetime import datetime

        section = self._work_section_text(text)
        if not section:
            return None

        date_range_re = re.compile(
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4})'
            r'\s*[–—\-]+\s*'
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}|Present|Current)',
            re.IGNORECASE,
        )

        def parse_date(s: str) -> datetime | None:
            m = re.match(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+(\d{4})', s.strip().lower())
            if m:
                return datetime(int(m.group(2)), self._MONTH_MAP[m.group(1)[:3]], 1)
            return None

        now = datetime.now()
        total_months = 0

        for m in date_range_re.finditer(section):
            start = parse_date(m.group(1))
            end_str = m.group(2).strip().lower()
            end = now if end_str in ("present", "current") else parse_date(m.group(2))
            if start and end:
                months = (end.year - start.year) * 12 + (end.month - start.month)
                if months > 0:
                    total_months += months

        if not total_months:
            return None

        years, months = divmod(total_months, 12)
        if years and months:
            return f"{years} yr{'s' if years != 1 else ''} {months} mo"
        if years:
            return f"{years} year{'s' if years != 1 else ''}"
        return f"{months} month{'s' if months != 1 else ''}"

    def _clean(self, label: str, value: str) -> str:
        import re
        # Strip short section-label prefixes like "Libraries/Frameworks: " or
        # "Languages and Databases: " (max 4 words before the colon).
        value = re.sub(r'^(?:\w+(?:[/ ]\w+){0,3}):\s*', '', value).strip()
        # For email fields, extract just the email address
        if "email" in label.lower():
            m = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', value)
            if m:
                return m.group()
        return value

    def _detect_type(self, text: str) -> str:
        lower = text.lower()
        scores: dict[str, int] = {t: 0 for t in _TYPE_SIGNALS}
        for doc_type, signals in _TYPE_SIGNALS.items():
            for signal in signals:
                if signal in lower:
                    scores[doc_type] += 1
        best_type = max(scores, key=lambda t: scores[t])
        return best_type if scores[best_type] > 0 else "general"
