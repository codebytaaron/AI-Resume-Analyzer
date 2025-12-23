import re
from typing import List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


STOP = set(
    """
a an the and or but if then else when while for to of in on at by from with without
is are was were be been being as it this that these those you your we our they their
i me my he him his she her hers them who whom which what where why how
""".split()
)


ROLE_KEYWORDS = {
    "software engineer": [
        "python", "java", "javascript", "typescript", "api", "backend", "frontend", "sql",
        "git", "docker", "testing", "ci/cd", "aws", "gcp", "linux", "react", "node",
        "flask", "fastapi", "django", "kubernetes"
    ],
    "data analyst": [
        "sql", "excel", "tableau", "power bi", "python", "pandas", "statistics",
        "dashboards", "etl", "reporting", "forecasting", "a/b testing"
    ],
    "product manager": [
        "roadmap", "requirements", "stakeholders", "metrics", "go-to-market",
        "user research", "prioritization", "launch", "kpi", "strategy"
    ],
    "ml engineer": [
        "pytorch", "tensorflow", "training", "inference", "feature engineering",
        "model deployment", "mlops", "vector", "embeddings", "evaluation"
    ],
}


def tokenize_keywords(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\#\./\s-]", " ", text)
    parts = re.split(r"\s+", text)
    toks = []
    for p in parts:
        p = p.strip("-")
        if not p or p in STOP:
            continue
        if len(p) <= 2:
            continue
        toks.append(p)
    return toks


def get_reference_text(target_role: str, jd_text: str) -> str:
    if jd_text.strip():
        return jd_text
    role = target_role.strip().lower()
    for k, kws in ROLE_KEYWORDS.items():
        if k in role:
            return " ".join(kws)
    # fallback: just use role words
    return target_role


def keyword_alignment(resume_text: str, reference_text: str, top_k_missing: int = 25) -> dict:
    resume_text = resume_text.strip()
    reference_text = reference_text.strip()

    if not resume_text or not reference_text:
        return {
            "similarity": 0.0,
            "matched_count": 0,
            "missing_count": 0,
            "missing_keywords": [],
        }

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000,
    )
    X = vectorizer.fit_transform([resume_text, reference_text])
    sim = float(cosine_similarity(X[0], X[1])[0][0])

    vocab = np.array(vectorizer.get_feature_names_out())
    ref_vec = X[1].toarray().ravel()
    res_vec = X[0].toarray().ravel()

    # identify "important in reference but low/absent in resume"
    missing_mask = (ref_vec > 0.0) & (res_vec < (0.15 * ref_vec + 1e-9))
    missing_idxs = np.where(missing_mask)[0]

    # rank by reference tf-idf weight
    ranked = sorted(
        [(vocab[i], float(ref_vec[i])) for i in missing_idxs],
        key=lambda x: x[1],
        reverse=True,
    )

    # matched keywords count (rough)
    matched_mask = (ref_vec > 0.0) & (res_vec > 0.0)
    matched_count = int(np.sum(matched_mask))
    missing_count = int(len(ranked))

    # trim + dedupe near-duplicates
    seen = set()
    missing_out: List[Tuple[str, float]] = []
    for kw, score in ranked:
        key = kw.replace(" ", "")
        if key in seen:
            continue
        seen.add(key)
        missing_out.append((kw, score))
        if len(missing_out) >= top_k_missing:
            break

    return {
        "similarity": sim,
        "matched_count": matched_count,
        "missing_count": missing_count,
        "missing_keywords": missing_out,
    }
