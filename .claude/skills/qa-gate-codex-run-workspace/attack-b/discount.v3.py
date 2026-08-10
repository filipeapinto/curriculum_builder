def apply_discount(price, pct):
    """Return price reduced by pct percent."""
    return round(price * (1 - pct / 100.0), 2)
