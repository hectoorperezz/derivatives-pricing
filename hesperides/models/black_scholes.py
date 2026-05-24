# hesperides/models/black_scholes.py

from dataclasses import dataclass


@dataclass(frozen=True)
class BlackScholesModel:
    """Black-Scholes risk-neutral lognormal model."""

    sigma: float
