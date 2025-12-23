import re
from typing import List, Tuple


EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b")
PHONE_RE = re.compile(
    r"(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*\d{3}\s*\)|\d{3})\s*(?:[.-]\s*)?)\d{3}\s*(?:[.-]\s*)?\d{4}"
)
URL_RE = re.compile(r"\bhttps?://[^\s)]+|\bwww\.[^\s)]+", re.IGNORECASE)
ZIP_RE = re.compile(r"\b\d{5}(?:-\d{4})?\b")
METRIC_RE = re.compile(r"(\b\d+(\.\d+)?%?\b)|(\b\$?\d+(?:,\d{3})+(?:\.\d+)?\b)")
BULLET_RE = re.compile(r"^\s*([•\-\u2022]|\d+\.)\s+")


def normalize_whitespace(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_lines(text: str) -> List[str]:
    return [ln.rstrip() for ln in text.splitlines()]


def is_bullet_line(line: str) -> bool:
    return bool(BULLET_RE.match(line))


def strip_bullet(line: str) -> str:
    return BULLET_RE.sub("", line).strip()


def find_contact_signals(text: str) -> dict:
    return {
        "email": bool(EMAIL_RE.search(text)),
        "phone": bool(PHONE_RE.search(text)),
        "url": bool(URL_RE.search(text)),
        "zip": bool(ZIP_RE.search(text)),
    }


def count_metrics(text: str) -> int:
    return len(METRIC_RE.findall(text))


def extract_bullets(text: str, max_bullets: int = 80) -> List[str]:
    bullets = []
    for ln in split_lines(text):
        if is_bullet_line(ln):
            b = strip_bullet(ln)
            if b and len(b) >= 8:
                bullets.append(b)
        if len(bullets) >= max_bullets:
            break
    return bullets


def detect_sections(text: str) -> List[str]:
    # very lightweight section detector
    headers = [
        "education",
        "experience",
        "projects",
        "skills",
        "certifications",
        "awards",
        "leadership",
        "summary",
        "objective",
        "activities",
        "volunteering",
    ]
    found = set()
    for ln in split_lines(text):
        clean = re.sub(r"[^a-zA-Z ]", "", ln).strip().lower()
        if 2 <= len(clean) <= 30:
            for h in headers:
                if clean == h or clean.startswith(h + " "):
                    found.add(h)
    return sorted(found)


ACTION_VERBS = {
    "built", "created", "designed", "developed", "shipped", "launched", "led", "managed",
    "owned", "improved", "optimized", "automated", "implemented", "delivered", "analyzed",
    "measured", "deployed", "trained", "tested", "refactored", "scaled", "reduced",
    "increased", "grew", "boosted", "collaborated", "coordinated", "presented",
    "researched", "engineered", "integrated", "maintained", "migrated", "streamlined",
    "executed", "spearheaded"
}


def bullet_quality_signals(bullet: str) -> Tuple[bool, bool, bool]:
    # Returns: starts_with_action, has_metric, has_specificity
    words = re.findall(r"[A-Za-z]+", bullet.lower())
    starts_action = bool(words) and words[0] in ACTION_VERBS
    has_metric = bool(METRIC_RE.search(bullet))
    has_specificity = len(words) >= 10  # crude heuristic
    return starts_action, has_metric, has_specificity


def clamp(n: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, n))
