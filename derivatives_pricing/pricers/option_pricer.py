# derivatives_pricing/pricers/option_pricer.py

from derivatives_pricing.contracts.base import Option
from derivatives_pricing.engines.base import Engine
from derivatives_pricing.market.data import MarketData
from derivatives_pricing.pricers.base import Pricer


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
