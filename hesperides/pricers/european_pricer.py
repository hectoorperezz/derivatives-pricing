# hesperides/pricers/european_pricer.py

from hesperides.pricers.base import Pricer
from hesperides.contracts.base import Option
from hesperides.market.base import DiscountCurve
from hesperides.models.base import Model
from hesperides.engines.base import Engine


class EuropeanPricer(Pricer):
    """Orchestrates pricing of European options."""

    def __init__(self, contract: Option, model: Model,
                 curve: DiscountCurve, engine: Engine):
        self.contract = contract
        self.model = model
        self.curve = curve
        self.engine = engine

    def price(self, St: float) -> float:
        """Compute option price."""
        return self.engine.price(self.contract, self.model, self.curve, St)