# hesperides/contracts/asian.py

from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

from hesperides.contracts.base import Option


@dataclass(frozen=True)
class GeometricAsianOption(Option):
    """Geometric Asian option with continuous-average analytical payoff."""

    K: float
    expiry: float
    call: bool

    def payoff(self, G_T: NDArray[np.float64]) -> NDArray[np.float64]:
        """Compute payoff from geometric averages G_T."""
        if self.call:
            return np.maximum(G_T - self.K, 0.0)
        return np.maximum(self.K - G_T, 0.0)
