from typing import List, Dict
from .utils import bullet_quality_signals, METRIC_RE

DEFAULT_ACTIONS = [
    "Built", "Designed", "Developed", "Implemented", "Led", "Optimized", "Automated",
    "Improved", "Deployed", "Analyzed", "Streamlined", "Integrated"
]


def make_rewrite(bullet: str) -> str:
    # Offline, rule-based rewrite: action + what + impact + metric placeholder if missing
    starts_action, has_metric, has_specificity = bullet_quality_signals(bullet)

    base = bullet.strip()
    if not base:
        return bullet

    # ensure action verb start (very light)
    if not starts_action:
        base = f"{DEFAULT_ACTIONS[0]} {base[0].lower() + base[1:]}" if len(base) > 1 else f"{DEFAULT_ACTIONS[0]} {base}"

    # if no metric, add a non-fake placeholder
    if not has_metric:
        base = base.rstrip(".")
        base += " resulting in [measurable outcome], improving [metric] by [X%/X]."

    # if too short, add clarity prompt
    if not has_specificity:
        base = base.rstrip(".")
        base += " using [tool/technique] across [scope/users/data]."

    # avoid double placeholders if already has numbers
    if METRIC_RE.search(bullet):
        base = base.replace("improving [metric] by [X%/X].", "improving key metrics.")

    return base


def generate_rewrites(bullets: List[str], max_items: int = 20) -> List[Dict[str, str]]:
    out = []
    for b in bullets[:max_items]:
        out.append({"original": b, "rewrite": make_rewrite(b)})
    return out
