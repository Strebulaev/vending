"""Currency normalization for the water vending project."""

# Reference rates (October 2026)
# Source: National Bank of Serbia, mid-market rate
EUR_TO_RSD = 117.0
USD_TO_RSD = 107.0


def to_rsd(amount: float, currency: str) -> float:
    """Convert amount in given currency to RSD."""
    if currency == "RSD":
        return amount
    if currency == "EUR":
        return amount * EUR_TO_RSD
    if currency == "USD":
        return amount * USD_TO_RSD
    raise ValueError(f"Unknown currency: {currency}")


def to_eur(amount: float, currency: str) -> float:
    """Convert amount in given currency to EUR."""
    if currency == "EUR":
        return amount
    if currency == "RSD":
        return amount / EUR_TO_RSD
    if currency == "USD":
        return amount * USD_TO_RSD / EUR_TO_RSD
    raise ValueError(f"Unknown currency: {currency}")