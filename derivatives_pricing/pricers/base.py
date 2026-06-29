# derivatives_pricing/pricers/base.py

from abc import ABC, abstractmethod


class Pricer(ABC):
    """Base class for all pricers."""

    @abstractmethod
    def price(self) -> float:
        """Compute the price of the instrument."""
        ...
