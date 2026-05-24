# hesperides/api.py

__all__ = [
    "get_price_binomial_european",
    "get_price_bs_european",
    "get_price_bs_geometric_asian",
    "compute_static_arbitrage_quantity",
]

import numpy as np

from hesperides.contracts.asian import GeometricAsianOption
from hesperides.contracts.european import EuropeanOption
from hesperides.engines.bs_analytical_engine import BlackScholesAnalyticalEngine
from hesperides.engines.bs_monte_carlo_engine import BlackScholesMonteCarloEngine
from hesperides.market.call_surface import CallSurface
from hesperides.market.curves import FlatDiscountCurve
from hesperides.market.data import MarketData
from hesperides.models.black_scholes import BlackScholesModel
from hesperides.models.binomial import BinomialModel
from hesperides.engines.binomial_engine import BinomialTreeEngine
from hesperides.pricers.option_pricer import OptionPricer


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
    engine = BinomialTreeEngine()
    pricer = OptionPricer(contract, model, market, engine)

    return pricer.price()


def get_price_bs_european(
    St: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    call: bool,
    engine: str = "analytical",
    n_paths: int | None = None,
    seed: int | None = None,
) -> float:
    """Price a European call or put option under Black-Scholes."""
    contract = EuropeanOption(K=K, expiry=T, call=call)
    market = MarketData(
        spot=St,
        curve=FlatDiscountCurve(R=r, compounding="continuous"),
    )
    model = BlackScholesModel(sigma=sigma)
    pricing_engine = _black_scholes_engine(engine, n_paths=n_paths, seed=seed)
    pricer = OptionPricer(contract, model, market, pricing_engine)
    return pricer.price()


def get_price_bs_geometric_asian(
    St: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    call: bool,
    engine: str = "analytical",
    n_paths: int | None = None,
    n_steps: int | None = None,
    seed: int | None = None,
) -> float:
    """Price a geometric Asian call or put option under Black-Scholes."""
    contract = GeometricAsianOption(K=K, expiry=T, call=call)
    market = MarketData(
        spot=St,
        curve=FlatDiscountCurve(R=r, compounding="continuous"),
    )
    model = BlackScholesModel(sigma=sigma)
    pricing_engine = _black_scholes_engine(
        engine, n_paths=n_paths, n_steps=n_steps, seed=seed
    )
    pricer = OptionPricer(contract, model, market, pricing_engine)
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


def _black_scholes_engine(
    engine: str,
    n_paths: int | None = None,
    n_steps: int | None = None,
    seed: int | None = None,
):
    if engine == "analytical":
        return BlackScholesAnalyticalEngine()
    if engine == "mc":
        if n_paths is None:
            raise ValueError("n_paths is required when engine='mc'.")
        return BlackScholesMonteCarloEngine(
            n_paths=n_paths,
            n_steps=n_steps,
            seed=seed,
        )
    raise ValueError("engine must be 'analytical' or 'mc'.")
