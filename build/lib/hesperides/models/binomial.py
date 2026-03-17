# hesperides/models/binomial.py

from dataclasses import dataclass
from hesperides.models.base import Model
from hesperides.market.base import DiscountCurve

@dataclass(frozen=True)
class BinomialModel(Model):
    """Binomial tree model. Defines up/down factors and risk-neutral dynamics."""

    u: float
    d: float

    def risk_neutral_prob(self, curve: DiscountCurve, t: int) -> float:
        """Risk-neutral probability of an up move at period t."""
        R = curve.rate(t)
        return (1 + R - self.d) / (self.u - self.d)