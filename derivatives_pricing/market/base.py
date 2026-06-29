# derivatives_pricing/market/base.py

from abc import ABC, abstractmethod


class DiscountCurve(ABC):
    """Base class for all discount curves."""

    @abstractmethod
    def rate(self, t: float) -> float:
        """Risk-free rate at period t."""
        ...

    @abstractmethod
    def discount_factor(self, t: float) -> float:
        """Present value of 1 unit received at period t."""
        ...
