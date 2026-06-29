# derivatives_pricing/models/black_scholes.py

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class BlackScholesModel:
    """Black-Scholes risk-neutral lognormal model with continuous yield."""

    sigma: float
    q: float = 0.0

    def cost_of_carry(self, r: float) -> float:
        """Return the risk-neutral drift contribution ``r - q``.

        Args:
            r: Continuously compounded risk-free rate.

        Returns:
            Cost of carry used in the Black-Scholes drift.
        """
        return r - self.q

    def yield_discount_factor(self, T: float) -> float:
        """Return the continuous-yield discount factor.

        Args:
            T: Time horizon.

        Returns:
            Factor ``exp(-q T)``.
        """
        return math.exp(-self.q * T)
