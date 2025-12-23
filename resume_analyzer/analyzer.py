from typing import Dict, List
import traceback

import pdfplumber
from PyPDF2 import PdfReader

from .utils import normalize_whitespace, extract_bullets, bullet_quality_signals
from .keywords import get_reference_text, keyword_alignment
from .scoring import score_resume
from .rewrite import generate_rewrites


def extract_text_from_pdf(pdf_path: str) -> str:
    # Try pdfplumber first (often best), fallback to PyPDF2
    texts: List[str] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                if t.strip():
                    texts.append(t)
    except Exception:
        # fallback
        pass

    joined = "\n".join(texts).strip()
    if joined:
        return joined

    # PyPDF2 fallback
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                texts.append(t)
        return "\n".join(texts).strip()
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")


def strengths_weaknesses(resume_text: str, score_obj: Dict, kw_obj: Dict) -> Dict[str, List[str]]:
    strengths: List[str] = []
    weaknesses: List[str] = []

    sig = score_obj["signals"]

    # Strengths
    if sig["contact"]["email"] and sig["contact"]["phone"]:
        strengths.append("Has clear contact info (email + phone).")
    if len(sig["sections"]) >= 3:
        strengths.append(f"Good structure with sections: {', '.join(sig['sections'])}.")
    if sig["metrics_found"] >= 3:
        strengths.append("Uses metrics to show impact.")
    if sig["action_rate"] >= 0.5:
        strengths.append("Many bullets start with strong action verbs.")
    if kw_obj["similarity"] >= 0.35:
        strengths.append("Decent alignment with the target role / job description.")

    # Weaknesses
    if not sig["contact"]["url"]:
        weaknesses.append("No portfolio/LinkedIn link detected. Consider adding one.")
    if sig["metrics_found"] == 0:
        weaknesses.append("No measurable outcomes found. Add numbers to prove impact.")
    if sig["action_rate"] < 0.45:
        weaknesses.append("Too many bullets do not start with action verbs.")
    if sig["specific_rate"] < 0.55:
        weaknesses.append("Bullets could be more specific (tools, scope, results).")
    if kw_obj["similarity"] < 0.25:
        weaknesses.append("Low keyword alignment. Tailor skills and wording to the role/JD.")

    # Always keep at least 2 each if possible
    if not strengths:
        strengths.append("Resume text extracted successfully.")
    if not weaknesses:
        weaknesses.append("No major red flags detected from basic heuristics.")

    return {"strengths": strengths, "weaknesses": weaknesses}


def bullet_suggestions(resume_text: str, max_items: int = 15) -> List[Dict]:
    bullets = extract_bullets(resume_text)
    out: List[Dict] = []

    for b in bullets:
        starts_action, has_metric, has_specificity = bullet_quality_signals(b)
        sugg = []
        if not starts_action:
            sugg.append("Start with a strong action verb (Built, Led, Designed, Automated, Improved).")
        if not has_specificity:
            sugg.append("Add tools/tech + scope (what you used and what you touched).")
        if not has_metric:
            sugg.append("Add a measurable result (%, $, time saved, scale, counts).")

        if sugg:
            out.append({"original": b, "suggestions": sugg})

        if len(out) >= max_items:
            break
    return out


def render_report_text(result: Dict) -> str:
    lines = []
    lines.append("AI Resume Analyzer Report")
    lines.append("=" * 28)
    lines.append("")
    lines.append(f"Overall Score: {result['score']['overall']}/100 (Grade {result['score']['grade']})")
    lines.append("")

    lines.append("Score Breakdown")
    lines.append("-" * 14)
    for row in result["score"]["breakdown"]:
        lines.append(f"- {row['category']}: {row['points']}  |  {row['notes']}")
    lines.append("")

    lines.append("Strengths")
    lines.append("-" * 9)
    for s in result["strengths"]:
        lines.append(f"- {s}")
    lines.append("")

    lines.append("Weaknesses")
    lines.append("-" * 10)
    for w in result["weaknesses"]:
        lines.append(f"- {w}")
    lines.append("")

    ka = result["keyword_alignment"]
    lines.append("Keyword Alignment")
    lines.append("-" * 16)
    lines.append(f"Similarity (TF-IDF cosine): {ka['similarity']:.3f}")
    lines.append(f"Matched keywords: {ka['matched_count']}")
    lines.append(f"Missing keywords: {ka['missing_count']}")
    if ka["missing_keywords"]:
        lines.append("")
        lines.append("Top Missing Keywords:")
        for kw, sc in ka["missing_keywords"]:
            lines.append(f"- {kw} ({sc:.3f})")
    lines.append("")

    if result["bullet_suggestions"]:
        lines.append("Bullet Suggestions")
        lines.append("-" * 16)
        for item in result["bullet_suggestions"]:
            lines.append(f"Original: {item['original']}")
            for s in item["suggestions"]:
                lines.append(f"  - {s}")
            lines.append("")

    if result.get("rewrites"):
        lines.append("Optional Bullet Rewrites (Offline)")
        lines.append("-" * 32)
        for item in result["rewrites"]:
            lines.append(f"Original: {item['original']}")
            lines.append(f"Rewrite:  {item['rewrite']}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def analyze_resume(
    pdf_path: str,
    target_role: str = "",
    job_description_text: str = "",
    top_k_missing: int = 25,
    generate_rewrites: bool = False,
) -> Dict:
    try:
        raw_text = extract_text_from_pdf(pdf_path)
        resume_text = normalize_whitespace(raw_text)

        reference_text = get_reference_text(target_role, job_description_text)
        kw = keyword_alignment(resume_text, reference_text, top_k_missing=top_k_missing)

        score = score_resume(resume_text, kw["similarity"])
        sw = strengths_weaknesses(resume_text, score, kw)

        bullets = extract_bullets(resume_text)
        suggestions = bullet_suggestions(resume_text)

        rewrites = generate_rewrites(bullets) if generate_rewrites else None

        result = {
            "score": score,
            "strengths": sw["strengths"],
            "weaknesses": sw["weaknesses"],
            "keyword_alignment": kw,
            "bullet_suggestions": suggestions,
        }
        if rewrites:
            result["rewrites"] = rewrites

        result["report_text"] = render_report_text(result)
        return result

    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc(),
            "score": {"overall": 0, "grade": "F", "breakdown": []},
            "strengths": [],
            "weaknesses": ["Analyzer crashed. Check PDF text extraction and dependencies."],
            "keyword_alignment": {"similarity": 0.0, "matched_count": 0, "missing_count": 0, "missing_keywords": []},
            "bullet_suggestions": [],
            "report_text": f"ERROR: {e}\n\n{traceback.format_exc()}",
        }
