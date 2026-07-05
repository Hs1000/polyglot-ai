import logging
import re

from app.services.tech_vocab import (
    KNOWN_DATABASES, KNOWN_FRAMEWORKS, KNOWN_LANGUAGES,
    normalise, scan_for_known, tokenise,
)

logger = logging.getLogger(__name__)

# Questions to extract requirements from a job description.
_JD_SCHEMA = {
    "Role Title":              "What is the job title or role being hired for?",
    "Required Languages":      "What programming or scripting languages such as Python, Java, JavaScript, Go, SQL, C++ are required?",
    "Required Frameworks":     "What software frameworks or libraries such as React, Django, Flask, TensorFlow, PyTorch, Spring are required?",
    "Min Years of Experience": "How many years of experience are required?",
    "Required Degree":         "What degree or education level such as Bachelor's, Master's, or PhD is required?",
    "Key Skills":              "What are the key technical skills required?",
}

# Degree level mapping for comparison
_DEGREE_LEVELS = {
    "high school": 0, "associate": 1, "bachelor": 2, "bs": 2, "ba": 2,
    "undergraduate": 2, "master": 3, "ms": 3, "msc": 3, "mba": 3,
    "phd": 4, "doctorate": 4, "doctoral": 4,
}

# Convenience wrappers that keep call sites unchanged
def _normalise(text: str) -> str:
    return normalise(text)

def _tokenise_list(value: str | None) -> list[str]:
    return tokenise(value)


def _parse_years(text: str | None) -> float | None:
    """Extract the minimum years requirement as a float."""
    if not text:
        return None
    # "3+ years", "3 years", "3 yrs", "three years"
    m = re.search(r'(\d+(?:\.\d+)?)\s*\+?\s*(?:yr|year|yrs|years)', text, re.IGNORECASE)
    if m:
        return float(m.group(1))
    # Bare "3+" or just "3"
    m = re.search(r'(\d+(?:\.\d+)?)\s*\+?', text)
    return float(m.group(1)) if m else None


def _parse_resume_years(text: str | None) -> float | None:
    """Parse 'X yrs Y mo' format from resume extraction."""
    if not text:
        return None
    years, months = 0.0, 0.0
    ym = re.search(r'(\d+)\s*yr', text, re.IGNORECASE)
    mm = re.search(r'(\d+)\s*mo', text, re.IGNORECASE)
    if ym:
        years = float(ym.group(1))
    if mm:
        months = float(mm.group(1))
    return years + months / 12 if (ym or mm) else None


def _degree_level(text: str | None) -> int | None:
    if not text:
        return None
    t = text.lower()
    for key, level in _DEGREE_LEVELS.items():
        if key in t:
            return level
    return None


class MatchingService:

    def __init__(self):
        self._extraction_service = None

    def _get_extraction_service(self):
        if self._extraction_service is None:
            from app.services.extraction_service import ExtractionService
            self._extraction_service = ExtractionService()
        return self._extraction_service

    def _get_chat_service(self):
        from app.services.chat_service import get_chat_service
        return get_chat_service()

    # ── public API ────────────────────────────────────────────────────────────

    def match(self, resume_text: str, job_description: str) -> dict:
        resume_fields = self._extract_resume(resume_text)
        jd_fields     = self._extract_jd(job_description)
        comparisons   = self._compare(jd_fields, resume_fields)

        # Score: match=1pt, partial=0.5pt, missing=0pt; ignore not_specified
        scored = [c for c in comparisons if c["status"] != "not_specified"]
        if not scored:
            score = 0.0
        else:
            pts = sum(
                1.0 if c["status"] == "match" else
                0.5 if c["status"] == "partial" else 0.0
                for c in scored
            )
            score = pts / len(scored)

        matched = sum(1 for c in scored if c["status"] == "match")
        partial = sum(1 for c in scored if c["status"] == "partial")
        missing = sum(1 for c in scored if c["status"] == "missing")

        return {
            "match_score": round(score, 2),
            "matched": matched,
            "partial": partial,
            "missing": missing,
            "comparisons": comparisons,
        }

    # ── extraction ────────────────────────────────────────────────────────────

    def _extract_resume(self, text: str) -> dict:
        svc = self._get_extraction_service()
        result = svc.extract(text)
        f = result["fields"]
        return {
            "languages":  f.get("Programming Languages"),
            "frameworks": f.get("Frameworks"),
            "years":      f.get("Years of Experience"),
            "degree":     f.get("Degree"),
        }

    def _extract_jd(self, jd_text: str) -> dict:
        svc = self._get_chat_service()
        out = {}
        for label, question in _JD_SCHEMA.items():
            try:
                ans = svc.ask(jd_text, question)
                if "couldn't find" in ans.lower():
                    out[label] = None
                elif label == "Required Languages" and not self._has_known_token(ans, KNOWN_LANGUAGES):
                    out[label] = None  # QA picked up non-language text
                elif label == "Required Frameworks" and not self._has_known_token(ans, KNOWN_FRAMEWORKS):
                    out[label] = None  # QA picked up non-framework text
                else:
                    out[label] = ans
            except Exception:
                logger.exception("JD extraction failed for %r", label)
                out[label] = None

        # Validate degree: discard QA answer if it contains no degree keyword
        if out.get("Required Degree") and _degree_level(out["Required Degree"]) is None:
            out["Required Degree"] = None
        if not out.get("Required Degree"):
            out["Required Degree"] = self._regex_extract_degree(jd_text)

        # Bullet-point JDs often produce a mixed languages+frameworks answer for
        # one field and nothing for the other. Separate them by the known sets.
        if out.get("Required Languages") is None and out.get("Required Frameworks"):
            langs, fws = self._separate_lang_fw(out["Required Frameworks"])
            if langs:
                out["Required Languages"] = langs
            if fws:
                out["Required Frameworks"] = fws
        elif out.get("Required Frameworks") is None and out.get("Required Languages"):
            langs, fws = self._separate_lang_fw(out["Required Languages"])
            if langs:
                out["Required Languages"] = langs
            if fws:
                out["Required Frameworks"] = fws

        # Last resort: if BOTH are still None, mine "Key Skills" for tech tokens
        if out.get("Required Languages") is None and out.get("Required Frameworks") is None:
            key_skills = out.get("Key Skills")
            if key_skills and ("couldn't find" not in key_skills.lower()):
                langs, fws = self._separate_lang_fw(key_skills)
                if langs:
                    out["Required Languages"] = langs
                if fws:
                    out["Required Frameworks"] = fws

        # Absolute last resort: brute-force scan the full JD text.
        # Handles natural-language phrasing like "Proficient in Python, SQL, Go"
        # where QA never fires because there's no explicit label.
        if out.get("Required Languages") is None:
            found = scan_for_known(jd_text, KNOWN_LANGUAGES)
            if found:
                out["Required Languages"] = ", ".join(found)

        if out.get("Required Frameworks") is None:
            found = scan_for_known(jd_text, KNOWN_FRAMEWORKS)
            if found:
                out["Required Frameworks"] = ", ".join(found)

        return out

    def _regex_extract_degree(self, text: str) -> str | None:
        """Scan JD text for explicit degree mentions when QA fails."""
        pattern = re.compile(
            r"(phd|ph\.d|doctorate|master(?:'s)?(?:\s+of\s+\w+)?(?:\s+degree)?|"
            r"m\.s\.|msc|mba|bachelor(?:'s)?(?:\s+of\s+\w+)?(?:\s+degree)?|"
            r"b\.s\.|bsc|b\.a\.|associate(?:'s)?(?:\s+degree)?)",
            re.IGNORECASE,
        )
        m = pattern.search(text)
        return m.group(0).strip() if m else None

    def _separate_lang_fw(self, combined: str) -> tuple:
        """Split a mixed languages+frameworks string into two clean lists."""
        tokens = _tokenise_list(combined)
        langs = [t for t in tokens if t in KNOWN_LANGUAGES]
        fws   = [t for t in tokens if t in KNOWN_FRAMEWORKS]
        return (
            ", ".join(langs) if langs else None,
            ", ".join(fws)   if fws   else None,
        )

    def _has_known_token(self, value: str, known: set) -> bool:
        return any(t in known for t in _tokenise_list(value))

    # ── comparison ───────────────────────────────────────────────────────────

    def _compare(self, jd: dict, resume: dict) -> list[dict]:
        results = []

        # --- Programming Languages ---
        jd_langs = _tokenise_list(jd.get("Required Languages"))
        res_langs = _tokenise_list(resume.get("languages"))
        results.append(self._compare_list(
            "Programming Languages",
            jd_langs, jd.get("Required Languages"),
            res_langs, resume.get("languages"),
        ))

        # --- Frameworks / Libraries ---
        jd_fw = _tokenise_list(jd.get("Required Frameworks"))
        res_fw = _tokenise_list(resume.get("frameworks"))
        results.append(self._compare_list(
            "Frameworks & Libraries",
            jd_fw, jd.get("Required Frameworks"),
            res_fw, resume.get("frameworks"),
        ))

        # --- Years of Experience ---
        jd_yrs  = _parse_years(jd.get("Min Years of Experience"))
        res_yrs = _parse_resume_years(resume.get("years"))
        results.append(self._compare_years(
            jd_yrs, jd.get("Min Years of Experience"),
            res_yrs, resume.get("years"),
        ))

        # --- Degree ---
        jd_deg  = _degree_level(jd.get("Required Degree"))
        res_deg = _degree_level(resume.get("degree"))
        results.append(self._compare_degree(
            jd_deg, jd.get("Required Degree"),
            res_deg, resume.get("degree"),
        ))

        # --- Key Skills (informational, shown as-is) ---
        results.append({
            "field":        "Key Skills Required",
            "jd_value":     jd.get("Key Skills"),
            "resume_value": None,
            "status":       "not_specified",
            "detail":       None,
        })

        # --- Role Title (informational) ---
        results.append({
            "field":        "Role Title",
            "jd_value":     jd.get("Role Title"),
            "resume_value": None,
            "status":       "not_specified",
            "detail":       None,
        })

        return results

    def _compare_list(
        self,
        field: str,
        jd_tokens: list[str], jd_raw: str | None,
        res_tokens: list[str], res_raw: str | None,
    ) -> dict:
        if not jd_tokens:
            return {"field": field, "jd_value": None, "resume_value": res_raw,
                    "status": "not_specified", "detail": None}

        matched, missing = [], []
        for item in jd_tokens:
            found = any(item in r or r in item for r in res_tokens)
            (matched if found else missing).append(item)

        if not missing:
            status = "match"
            detail = f"All required: {', '.join(matched)}"
        elif matched:
            status = "partial"
            detail = f"Has: {', '.join(matched)} — Missing: {', '.join(missing)}"
        else:
            status = "missing"
            detail = f"Missing all: {', '.join(missing)}"

        return {"field": field, "jd_value": jd_raw, "resume_value": res_raw,
                "status": status, "detail": detail}

    def _compare_years(
        self,
        jd_yrs: float | None, jd_raw: str | None,
        res_yrs: float | None, res_raw: str | None,
    ) -> dict:
        field = "Years of Experience"
        if jd_yrs is None:
            return {"field": field, "jd_value": jd_raw, "resume_value": res_raw,
                    "status": "not_specified", "detail": None}
        if res_yrs is None:
            return {"field": field, "jd_value": jd_raw, "resume_value": res_raw,
                    "status": "missing", "detail": "Could not determine years from resume"}

        if res_yrs >= jd_yrs:
            status, detail = "match", f"{res_raw} meets {jd_raw}"
        elif res_yrs >= jd_yrs * 0.75:
            status = "partial"
            detail = f"{res_raw} — slightly below {jd_raw} requirement"
        else:
            status, detail = "missing", f"{res_raw} — below {jd_raw} requirement"

        return {"field": field, "jd_value": jd_raw, "resume_value": res_raw,
                "status": status, "detail": detail}

    def _compare_degree(
        self,
        jd_level: int | None, jd_raw: str | None,
        res_level: int | None, res_raw: str | None,
    ) -> dict:
        field = "Education / Degree"
        if jd_level is None:
            return {"field": field, "jd_value": jd_raw, "resume_value": res_raw,
                    "status": "not_specified", "detail": None}
        if res_level is None:
            return {"field": field, "jd_value": jd_raw, "resume_value": res_raw,
                    "status": "missing", "detail": "Could not determine degree from resume"}

        if res_level >= jd_level:
            status, detail = "match", f"{res_raw} meets requirement"
        else:
            status, detail = "missing", f"{res_raw} — below required {jd_raw}"

        return {"field": field, "jd_value": jd_raw, "resume_value": res_raw,
                "status": status, "detail": detail}
