from analyzer.scoring import score_resume
from analyzer.keywords import keyword_gap
from analyzer.bullets import analyze_bullets

def analyze_resume(resume_text: str, jd_text: str):
    score = score_resume(resume_text)
    missing_keywords = keyword_gap(resume_text, jd_text)
    weak_bullets = analyze_bullets(resume_text)

    return {
        "score": score,
        "missing_keywords": missing_keywords,
        "weak_bullets": weak_bullets,
        "summary": generate_summary(score["total"])
    }

def generate_summary(score: int):
    if score >= 85:
        return "Strong resume with minor optimization opportunities."
    if score >= 70:
        return "Solid foundation. Improvements needed to be competitive."
    if score >= 55:
        return "Below average. Significant revisions recommended."
    return "High risk resume. Major restructuring required."
