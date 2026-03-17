# hesperides/market/curves.py

from dataclasses import dataclass
from hesperides.market.base import DiscountCurve


@dataclass(frozen=True)
class FlatDiscountCurve(DiscountCurve):
    """Flat interest rate curve. Constant rate across all periods."""

    R: float

    def rate(self, t: int) -> float:
        """Risk-free rate at period t."""
        return self.R

    def discount_factor(self, t: int) -> float:
        """Present value of 1 unit received at period t."""
        return (1 + self.R) ** (-t)