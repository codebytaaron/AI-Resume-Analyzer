import re

def score_resume(text: str) -> dict:
    length_score = min(len(text) / 6000, 1.0) * 25

    metrics = len(re.findall(r"\d+%", text)) + len(re.findall(r"\d+\+", text))
    metric_score = min(metrics * 3, 25)

    verbs = len(re.findall(
        r"\b(built|led|designed|improved|analyzed|developed|launched|optimized)\b",
        text.lower()
    ))
    verb_score = min(verbs * 2, 25)

    section_score = 25 if "experience" in text.lower() and "education" in text.lower() else 12

    total = round(length_score + metric_score + verb_score + section_score)

    return {
        "total": min(total, 100),
        "breakdown": {
            "structure": round(section_score),
            "metrics": round(metric_score),
            "impact": round(verb_score),
            "length": round(length_score),
        }
    }
