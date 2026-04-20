# hesperides/pricers/european_pricer.py

from hesperides.pricers.base import Pricer
from hesperides.contracts.base import Option
from hesperides.market.data import MarketData
from hesperides.engines.base import Engine


class EuropeanPricer(Pricer):
    """Orchestrates pricing of European options."""

    def __init__(self, contract: Option, model,
                 market: MarketData, engine: Engine):
        self.contract = contract
        self.model = model
        self.market = market
        self.engine = engine

    def price(self) -> float:
        """Compute option price."""
        return self.engine.price(self.contract, self.model, self.market)
