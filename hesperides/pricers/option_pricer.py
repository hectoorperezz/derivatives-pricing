# hesperides/pricers/option_pricer.py

from hesperides.contracts.base import Option
from hesperides.engines.base import Engine
from hesperides.market.data import MarketData
from hesperides.pricers.base import Pricer


class OptionPricer(Pricer):
    """Orchestrates pricing of option contracts."""

    def __init__(self, contract: Option, model, market: MarketData, engine: Engine):
        self.contract = contract
        self.model = model
        self.market = market
        self.engine = engine

    def price(self) -> float:
        """Compute option price."""
        return self.engine.price(self.contract, self.model, self.market)
