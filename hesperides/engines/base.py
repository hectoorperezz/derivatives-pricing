# hesperides/engines/base.py

from abc import ABC, abstractmethod
from hesperides.contracts.base import Option
from hesperides.market.base import DiscountCurve


class Engine(ABC):
    """Base class for all pricing engines."""

    @abstractmethod
    def price(self, contract: Option, model, curve: DiscountCurve,
              St: float) -> float:
        """Compute the price of a derivative."""
        ...