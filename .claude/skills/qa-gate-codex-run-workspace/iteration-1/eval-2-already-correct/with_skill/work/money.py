from decimal import Decimal, ROUND_HALF_UP


def split_evenly(total, ways):
    """Split a Decimal amount into `ways` parts that sum exactly to total.
    Remainder cents are distributed one each to the earliest parts."""
    if ways < 1:
        raise ValueError("ways must be at least 1")
    cents = int((total * 100).to_integral_value(rounding=ROUND_HALF_UP))
    base, extra = divmod(cents, ways)
    return [Decimal(base + (1 if i < extra else 0)) / 100 for i in range(ways)]
