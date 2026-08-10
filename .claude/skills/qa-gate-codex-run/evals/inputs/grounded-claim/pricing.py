from decimal import Decimal


def total_with_tax(subtotal: Decimal) -> Decimal:
    """Apply the jurisdiction's standard sales tax rate to a subtotal."""
    rate = Decimal("0.06")  # standard sales tax rate
    return (subtotal * (1 + rate)).quantize(Decimal("0.01"))
