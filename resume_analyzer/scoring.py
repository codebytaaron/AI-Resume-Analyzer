from typing import Dict, List

from .utils import (
    normalize_whitespace,
    find_contact_signals,
    count_metrics,
    extract_bullets,
    detect_sections,
    bullet_quality_signals,
    clamp,
)


def score_resume(resume_text: str, keyword_similarity: float) -> Dict:
    t = normalize_whitespace(resume_text)
    length = len(t)
    words = len(t.split())

    contact = find_contact_signals(t)
    sections = detect_sections(t)
    bullets = extract_bullets(t)
    metric_count = count_metrics(t)

    # Bullet quality
    good_action = 0
    good_metric = 0
    good_specific = 0
    for b in bullets[:60]:
        a, m, s = bullet_quality_signals(b)
        good_action += 1 if a else 0
        good_metric += 1 if m else 0
        good_specific += 1 if s else 0

    total_bullets = max(len(bullets), 1)
    action_rate = good_action / total_bullets
    metric_rate = good_metric / total_bullets
    specific_rate = good_specific / total_bullets

    breakdown: List[Dict] = []
    points = 0.0

    # 1) Basic completeness (20)
    comp = 0.0
    notes = []
    if contact["email"]:
        comp += 6
    else:
        notes.append("Missing email")
    if contact["phone"]:
        comp += 6
    else:
        notes.append("Missing phone")
    if contact["url"]:
        comp += 4
    else:
        notes.append("No portfolio/LinkedIn link detected")
    if words >= 200:
        comp += 4
    else:
        notes.append("Resume text looks very short")
    comp = clamp(comp, 0, 20)
    points += comp
    breakdown.append(
        {"category": "Completeness", "points": round(comp, 1), "notes": ", ".join(notes) or "Solid basics"}
    )

    # 2) Structure / sections (20)
    struct = 0.0
    notes = []
    must = {"experience", "education", "skills"}
    hit = len(must.intersection(set(sections)))
    struct += hit * 6  # up to 18
    if "projects" in sections:
        struct += 2
    if struct < 12:
        notes.append("Add clearer section headers (Experience/Education/Skills)")
    struct = clamp(struct, 0, 20)
    points += struct
    breakdown.append(
        {"category": "Structure", "points": round(struct, 1), "notes": ", ".join(notes) or "Good section coverage"}
    )

    # 3) Bullet strength (25)
    bullet_pts = 0.0
    notes = []
    if len(bullets) >= 8:
        bullet_pts += 6
    else:
        notes.append("Add more bullets under roles/projects")
    bullet_pts += 10 * clamp(action_rate, 0, 1)  # action verbs
    bullet_pts += 7 * clamp(specific_rate, 0, 1)  # specificity
    bullet_pts += 2 * clamp(metric_rate, 0, 1)  # metrics inside bullets
    if action_rate < 0.45:
        notes.append("More bullets should start with strong action verbs")
    if specific_rate < 0.55:
        notes.append("More bullets should include tools/scope/results")
    bullet_pts = clamp(bullet_pts, 0, 25)
    points += bullet_pts
    breakdown.append(
        {"category": "Bullet Quality", "points": round(bullet_pts, 1), "notes": ", ".join(notes) or "Bullets are solid"}
    )

    # 4) Quantification (15)
    quant = 0.0
    notes = []
    if metric_count >= 6:
        quant = 15
    elif metric_count >= 3:
        quant = 11
    elif metric_count >= 1:
        quant = 7
        notes.append("Add more metrics (%, $, time saved, scale, counts)")
    else:
        quant = 3
        notes.append("Add measurable outcomes to bullets")
    points += quant
    breakdown.append({"category": "Quantification", "points": round(quant, 1), "notes": ", ".join(notes) or "Nice metrics"})

    # 5) Keyword alignment (20)
    # similarity is 0..1, map to 0..20
    kw = 20.0 * clamp(keyword_similarity, 0.0, 1.0)
    notes = []
    if kw < 10:
        notes.append("Tailor skills and bullets to the target role / JD keywords")
    points += kw
    breakdown.append({"category": "Keyword Alignment", "points": round(kw, 1), "notes": ", ".join(notes) or "Good match"})

    overall = int(round(clamp(points, 0, 100)))
    grade = (
        "A" if overall >= 90 else
        "B" if overall >= 80 else
        "C" if overall >= 70 else
        "D" if overall >= 60 else
        "F"
    )

    return {
        "overall": overall,
        "grade": grade,
        "breakdown": breakdown,
        "signals": {
            "word_count": words,
            "char_count": length,
            "sections": sections,
            "bullets_found": len(bullets),
            "metrics_found": metric_count,
            "action_rate": round(action_rate, 3),
            "metric_rate": round(metric_rate, 3),
            "specific_rate": round(specific_rate, 3),
            "contact": contact,
        },
    }
