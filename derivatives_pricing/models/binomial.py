# derivatives_pricing/models/binomial.py

from dataclasses import dataclass
from derivatives_pricing.market.base import DiscountCurve


@dataclass(frozen=True)
class BinomialModel:
    """Binomial tree model. Defines up/down factors and risk-neutral dynamics."""

    u: float
    d: float

    def risk_neutral_prob(self, curve: DiscountCurve, t: int) -> float:
        """Risk-neutral probability of an up move at period t."""
        R = curve.rate(t)
        return (1 + R - self.d) / (self.u - self.d)
