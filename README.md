# AI Resume Analyzer

This repository documents an AI-powered resume analysis tool built as a command-line system for evaluating and improving resumes using NLP and automation.

The full implementation is intentionally not public. This repo shares how the system works without distributing the code.

For access or a walkthrough, go to my link in bio.

---

## What It Does

The AI Resume Analyzer processes a PDF resume and returns:

- Overall resume score (0–100)
- Strengths and weaknesses
- Keyword alignment for specific roles
- Bullet point improvement suggestions
- Optional AI-assisted rewrites

No frontend. No accounts. CLI only.

---

## How It Works (High Level)

```text
PDF Resume
   ↓
Text Extraction
   ↓
Cleaning & Normalization
   ↓
Feature Analysis
   ↓
Scoring Engine
   ↓
Optional AI Rewrites
   ↓
Terminal Output
