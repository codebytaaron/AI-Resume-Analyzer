<!-- HERO -->
<p align="center">
  <img
    src="https://capsule-render.vercel.app/api?type=rect&height=220&color=0:020617,100:0f172a&text=AI%20Resume%20Analyzer&fontColor=ffffff&fontSize=52&fontAlign=50&fontAlignY=42&desc=CLI%20resume%20scoring%20and%20NLP%20analysis&descAlign=50&descAlignY=66"
    alt="AI Resume Analyzer"
  />
</p>

<!-- MOVING (not snake) -->
<p align="center">
  <img
    src="https://readme-typing-svg.demolab.com?font=Inter&size=18&pause=1200&color=94A3B8&center=true&vCenter=true&width=820&lines=Analyze+PDF+resumes+from+the+terminal.;Score+0%E2%80%93100+and+explain+why.;Keyword+alignment+%2B+bullet+improvements."
    alt="Typing animation"
  />
</p>

# AI Resume Analyzer

This repository documents an AI-powered resume analysis tool built as a command-line system for evaluating and improving resumes using NLP and automation.

The full implementation is intentionally not public. This repo explains how the system works without distributing the code.

For access or a walkthrough, use the link in my bio.

---

## What it does

The AI Resume Analyzer processes a PDF resume and returns:

- Overall resume score (0–100)
- Strengths and weaknesses
- Keyword alignment for specific roles
- Bullet point improvement suggestions
- Optional AI-assisted rewrites

No frontend. No accounts. CLI only.

---

## How it works (high level)

<!-- RELATED IMAGE (pipeline diagram rendered as an image) -->
<p align="center">
  <img
    src="https://mermaid.ink/img/pako:eNqNkE1PwzAMhv8K0m2s2m5sQyq0cQh0QG3WcWnTgQ2kYx0m0q2Qp9O3Vwqv0lq7f5w8kq2wJcVx2mK2o7Q0gGkqv8oP5b8f0i8k3pVd1r2Ywzq1k2mSxvKq6k3VtW7JY3Q5qG9m9oB4i8v3oJm5H1e9m8mWf8o2uN0m0yKcE8i4v2vJt0aJm0d2w0o1YgQy1Qv0Gf1gYk9Yc7qHq5f2rQk2w7mR9b7QYh3oG2h6mP3h3m7Qv8oG9p5yYJ9m3S2oG0c9n2mP7oZbYg?type=png"
    alt="Resume analysis pipeline"
    width="900"
  />
</p>

```txt
PDF Resume
  -> Text Extraction
    -> Cleaning & Normalization
      -> Feature Analysis
        -> Scoring Engine
          -> Optional AI Rewrites
            -> Terminal Output
