# hesperides/contracts/european.py

from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray
from hesperides.contracts.base import Option


@dataclass(frozen=True)
class EuropeanOption(Option):
    """European option contract. Defines payoff at expiry for a vanilla call or put."""

    K: float
    expiry: float
    call: bool

    def payoff(self, S_T: NDArray[np.float64]) -> NDArray[np.float64]:
        """Compute payoff at expiry given terminal underlying prices."""
        if self.call:
            return np.maximum(S_T - self.K, 0.0)
        return np.maximum(self.K - S_T, 0.0)
