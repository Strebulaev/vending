"""Currency normalization for the water vending project.

Rates of 2026-10-06 as reported by https://biznis.kurir.rs/novcanik/10124956/kursna-lista-nbs-za-6-oktobar-2026
(the page cites National Bank of Serbia data; the NBS site itself was not opened):
  official middle EUR rate 117.4601 RSD; indicative USD rate 104.7068 RSD.
Update here and re-run the scripts when a newer date is needed.
"""

EUR_TO_RSD = 117.4601
USD_TO_RSD = 104.7068


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
