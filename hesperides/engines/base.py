# hesperides/engines/base.py

from abc import ABC, abstractmethod
from hesperides.contracts.base import Option
from hesperides.market.data import MarketData


class Engine(ABC):
    """Base class for all pricing engines."""

    @abstractmethod
    def price(self, contract: Option, model, market: MarketData) -> float:
        """Compute the price of a derivative."""
        ...
