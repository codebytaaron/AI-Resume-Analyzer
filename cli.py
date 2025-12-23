#!/usr/bin/env python3
import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from resume_analyzer.analyzer import analyze_resume


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ai-resume-analyzer",
        description="CLI resume analyzer: score, strengths/weaknesses, keyword alignment, bullet suggestions, optional rewrites.",
    )
    p.add_argument("pdf", type=str, help="Path to resume PDF")
    p.add_argument(
        "--role",
        type=str,
        default="",
        help="Target role (e.g., 'Software Engineer Intern'). Used for keyword focus if --jd not provided.",
    )
    p.add_argument(
        "--jd",
        type=str,
        default="",
        help="Path to a job description .txt file (recommended for best keyword alignment).",
    )
    p.add_argument(
        "--top-k",
        type=int,
        default=25,
        help="How many top missing keywords to show (default: 25).",
    )
    p.add_argument(
        "--rewrite",
        action="store_true",
        help="Generate rule-based bullet rewrites (offline).",
    )
    p.add_argument(
        "--out",
        type=str,
        default="",
        help="Optional output report path (.txt). If not set, prints to terminal only.",
    )
    return p


def main():
    console = Console()
    args = build_parser().parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    jd_text = ""
    if args.jd:
        jd_path = Path(args.jd).expanduser().resolve()
        if not jd_path.exists():
            raise SystemExit(f"JD file not found: {jd_path}")
        jd_text = jd_path.read_text(encoding="utf-8", errors="ignore")

    result = analyze_resume(
        pdf_path=str(pdf_path),
        target_role=args.role.strip(),
        job_description_text=jd_text,
        top_k_missing=args.top_k,
        generate_rewrites=args.rewrite,
    )

    # Pretty terminal output
    score = result["score"]["overall"]
    grade = result["score"]["grade"]
    summary = f"Overall Score: {score}/100  |  Grade: {grade}"
    console.print(Panel(summary, title="AI Resume Analyzer", expand=False))

    # Score breakdown
    breakdown = Table(title="Score Breakdown", show_lines=False)
    breakdown.add_column("Category", style="bold")
    breakdown.add_column("Points")
    breakdown.add_column("Notes")
    for row in result["score"]["breakdown"]:
        breakdown.add_row(row["category"], str(row["points"]), row["notes"])
    console.print(breakdown)

    # Strengths/Weaknesses
    sw = Table(title="Strengths & Weaknesses", show_lines=True)
    sw.add_column("Strengths", style="green")
    sw.add_column("Weaknesses", style="red")
    strengths = result["strengths"]
    weaknesses = result["weaknesses"]
    max_len = max(len(strengths), len(weaknesses), 1)
    for i in range(max_len):
        sw.add_row(
            strengths[i] if i < len(strengths) else "",
            weaknesses[i] if i < len(weaknesses) else "",
        )
    console.print(sw)

    # Keyword alignment
    ka = result["keyword_alignment"]
    console.print(
        Panel(
            f"Similarity (TF-IDF cosine): {ka['similarity']:.3f}\n"
            f"Matched keywords: {ka['matched_count']}  |  Missing keywords: {ka['missing_count']}",
            title="Keyword Alignment",
            expand=False,
        )
    )

    if ka["missing_keywords"]:
        miss = Table(title="Top Missing Keywords", show_lines=False)
        miss.add_column("Keyword", style="bold")
        miss.add_column("Importance")
        for kw, score_ in ka["missing_keywords"]:
            miss.add_row(kw, f"{score_:.3f}")
        console.print(miss)

    # Bullet suggestions
    if result["bullet_suggestions"]:
        bs = Table(title="Bullet Point Suggestions", show_lines=True)
        bs.add_column("Original", style="bold")
        bs.add_column("Suggestions")
        for item in result["bullet_suggestions"][:12]:
            bs.add_row(item["original"], "\n".join(f"• {s}" for s in item["suggestions"]))
        console.print(bs)

    # Rewrites
    if result.get("rewrites"):
        rw = Table(title="Optional Bullet Rewrites (Offline)", show_lines=True)
        rw.add_column("Original", style="bold")
        rw.add_column("Rewrite")
        for item in result["rewrites"][:12]:
            rw.add_row(item["original"], item["rewrite"])
        console.print(rw)

    # Optional file output
    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.write_text(result["report_text"], encoding="utf-8")
        console.print(f"[bold]Saved report to:[/bold] {out_path}")


if __name__ == "__main__":
    main()
