RESUME_KEYWORDS = [
    "experience", "skilled", "proficient", "expertise", "years of experience",
    "software engineer", "data scientist", "developer", "bachelor", "master",
    "phd", "graduated", "university", "degree", "qualification", "competencies",
    "tech lead", "engineer", "analyst", "professional profile",
]

PRODUCT_KEYWORDS = [
    "price", "priced at", "features", "available in", "brand", "product",
    "specs", "retail", "color options", "display", "battery", "storage",
    "introducing", "releases", "top-rated", "premium",
    "laptop", "phone", "headphone", "monitor", "keyboard", "tablet",
]

BIO_KEYWORDS = [
    "passionate about", "ex-", "previously at", "former", "driving",
    "focused on", "track record", "alumni",
    "linkedin", "currently",
]


def classify_input(text):
    """Classify input text as resume, product, or bio based on keyword matching."""
    text_lower = text.lower()
    scores = {"resume": 0, "product": 0, "bio": 0}

    for kw in RESUME_KEYWORDS:
        if kw in text_lower:
            scores["resume"] += 1

    for kw in PRODUCT_KEYWORDS:
        if kw in text_lower:
            scores["product"] += 1

    for kw in BIO_KEYWORDS:
        if kw in text_lower:
            scores["bio"] += 1

    # bios tend to use | separators heavily
    if text.count("|") >= 3:
        scores["bio"] += 3

    # products mention dollar prices
    if "$" in text:
        scores["product"] += 3

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "resume"  # default fallback

    return best
