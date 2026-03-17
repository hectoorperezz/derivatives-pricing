# hesperides/contracts/base.py

from abc import ABC, abstractmethod
import numpy as np
from numpy.typing import NDArray


class Option(ABC):
    """Base class for all option contracts."""

    @abstractmethod
    def payoff(self, S_T: NDArray[np.float64]) -> NDArray[np.float64]:
        """Compute payoff given terminal prices."""
        ...