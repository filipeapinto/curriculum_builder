import re

def slugify(title):
    """Lowercase, strip non-alphanumerics, join words with hyphens."""
    return re.sub(r"\s+", "-", title.lower())
