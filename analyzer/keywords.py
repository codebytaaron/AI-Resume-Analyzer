def keyword_gap(resume_text: str, jd_text: str):
    if not jd_text:
        return []

    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())

    keywords = [w for w in jd_words if len(w) > 4]
    missing = [w for w in keywords if w not in resume_words]

    return sorted(set(missing))[:15]
