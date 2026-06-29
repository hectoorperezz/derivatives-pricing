# derivatives_pricing/market/curves.py

from dataclasses import dataclass
import math
from typing import Literal

from derivatives_pricing.market.base import DiscountCurve


@dataclass(frozen=True)
class FlatDiscountCurve(DiscountCurve):
    """Flat curve with configurable compounding convention."""

    R: float
    compounding: Literal["discrete", "continuous"] = "discrete"

    def rate(self, t: float) -> float:
        """Risk-free rate at period t."""
        return self.R

    def discount_factor(self, t: float) -> float:
        """Present value of 1 unit received at period t."""
        if self.compounding == "discrete":
            return (1 + self.R) ** (-t)
        if self.compounding == "continuous":
            return math.exp(-self.R * t)
        raise ValueError("compounding must be 'discrete' or 'continuous'.")
