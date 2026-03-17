# hesperides/market/base.py

from abc import ABC, abstractmethod


class DiscountCurve(ABC):
    """Base class for all discount curves."""

    @abstractmethod
    def rate(self, t: int) -> float:
        """Risk-free rate at period t."""
        ...

    @abstractmethod
    def discount_factor(self, t: int) -> float:
        """Present value of 1 unit received at period t."""
        ...