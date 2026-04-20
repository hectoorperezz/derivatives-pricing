# hesperides/api.py

__all__ = [
    "get_price_binomial_european",
    "compute_static_arbitrage_quantity",
]

import numpy as np

from hesperides.contracts.european import EuropeanOption
from hesperides.market.call_surface import CallSurface
from hesperides.market.curves import FlatDiscountCurve
from hesperides.market.data import MarketData
from hesperides.models.binomial import BinomialModel
from hesperides.engines.binomial_engine import AnalyticBinomialEngine
from hesperides.pricers.european_pricer import EuropeanPricer


def get_price_binomial_european(
    St: float,
    K: float,
    T: int,
    R: float,
    u: float,
    d: float,
    call: bool,
) -> float:
    """Price a European call or put option using the binomial model."""
    contract = EuropeanOption(K=K, expiry=T, call=call)
    market = MarketData(spot=St, curve=FlatDiscountCurve(R=R))
    model = BinomialModel(u=u, d=d)
    engine = AnalyticBinomialEngine()
    pricer = EuropeanPricer(contract, model, market, engine)

    return pricer.price()


def compute_static_arbitrage_quantity(
    surface: np.ndarray,
    strikes: np.ndarray | None = None,
    quantity: str = "vertical",
) -> np.ndarray:
    """Carr-Madan static-arbitrage spread grid on a discrete call surface."""
    call_surface = CallSurface(prices=surface, strikes=strikes)
    if quantity == "vertical":
        return call_surface.vertical_spreads()
    if quantity == "butterfly":
        return call_surface.butterfly_values()
    if quantity == "calendar":
        return call_surface.calendar_spreads()
    raise ValueError(
        f"Invalid quantity: {quantity!r}. "
        "Expected 'vertical', 'butterfly', or 'calendar'."
    )
