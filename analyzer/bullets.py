import re

def analyze_bullets(text: str):
    bullets = [b.strip() for b in text.split("\n") if b.strip().startswith(("-", "•"))]

    weak = []
    for b in bullets:
        if not any(char.isdigit() for char in b):
            weak.append(b)

    return weak[:8]
