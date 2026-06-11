# hesperides/api.py

__all__ = [
    "get_price_binomial_european",
    "get_price_bs_european",
    "get_price_bs_european_dividend",
    "get_price_fx_option",
    "get_price_future_option",
    "get_price_bs_geometric_asian",
    "get_greek_bs_european",
    "compute_static_arbitrage_quantity",
]

import numpy as np

from hesperides.contracts.asian import GeometricAsianOption
from hesperides.contracts.european import EuropeanOption
from hesperides.engines.bs_analytical_engine import BlackScholesAnalyticalEngine
from hesperides.engines.bs_monte_carlo_engine import BlackScholesMonteCarloEngine
from hesperides.greeks.analytical import AnalyticalGreeks
from hesperides.greeks.finite_difference import FiniteDifferenceGreeks
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


def get_price_bs_european_dividend(
    St: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    call: bool,
    q: float = 0.0,
    engine: str = "analytical",
    n_paths: int | None = None,
    seed: int | None = None,
) -> float:
    """Price a European option with a continuous dividend yield.

    Args:
        St: Spot price of the underlying.
        K: Strike.
        T: Time to maturity in years.
        r: Continuously compounded risk-free rate.
        sigma: Annualized Black-Scholes volatility.
        call: True for call, False for put.
        q: Continuous dividend yield.
        engine: Pricing engine: ``"analytical"`` or ``"mc"``.
        n_paths: Number of Monte Carlo paths when ``engine="mc"``.
        seed: Optional Monte Carlo seed.

    Returns:
        Option price at valuation date.
    """
    _validate_cost_of_carry_request(
        St=St,
        K=K,
        T=T,
        sigma=sigma,
        engine=engine,
        n_paths=n_paths,
    )
    contract = EuropeanOption(K=K, expiry=T, call=call)
    market = MarketData(
        spot=St,
        curve=FlatDiscountCurve(R=r, compounding="continuous"),
    )
    model = BlackScholesModel(sigma=sigma, q=q)
    pricing_engine = _black_scholes_engine(engine, n_paths=n_paths, seed=seed)
    pricer = OptionPricer(contract, model, market, pricing_engine)
    return pricer.price()


def get_price_fx_option(
    St: float,
    K: float,
    T: float,
    r_d: float,
    r_f: float,
    sigma: float,
    call: bool,
    engine: str = "analytical",
    n_paths: int | None = None,
    seed: int | None = None,
) -> float:
    """Price a European FX option under Garman-Kohlhagen.

    Args:
        St: FX spot, quoted as domestic currency per unit of foreign currency.
        K: Strike in the same quotation convention as ``St``.
        T: Time to maturity in years.
        r_d: Continuously compounded domestic risk-free rate.
        r_f: Continuously compounded foreign risk-free rate.
        sigma: Annualized FX volatility.
        call: True for call, False for put.
        engine: Pricing engine: ``"analytical"`` or ``"mc"``.
        n_paths: Number of Monte Carlo paths when ``engine="mc"``.
        seed: Optional Monte Carlo seed.

    Returns:
        Option price at valuation date in domestic currency.
    """
    return get_price_bs_european_dividend(
        St=St,
        K=K,
        T=T,
        r=r_d,
        sigma=sigma,
        call=call,
        q=r_f,
        engine=engine,
        n_paths=n_paths,
        seed=seed,
    )


def get_price_future_option(
    F0: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    call: bool,
    engine: str = "analytical",
    n_paths: int | None = None,
    seed: int | None = None,
) -> float:
    """Price a European option on a future under Black-76.

    Args:
        F0: Current future price.
        K: Strike.
        T: Time to maturity in years.
        r: Continuously compounded risk-free rate.
        sigma: Annualized future volatility.
        call: True for call, False for put.
        engine: Pricing engine: ``"analytical"`` or ``"mc"``.
        n_paths: Number of Monte Carlo paths when ``engine="mc"``.
        seed: Optional Monte Carlo seed.

    Returns:
        Option price at valuation date.
    """
    if F0 <= 0:
        raise ValueError("Future price must be positive.")
    return get_price_bs_european_dividend(
        St=F0,
        K=K,
        T=T,
        r=r,
        sigma=sigma,
        call=call,
        q=r,
        engine=engine,
        n_paths=n_paths,
        seed=seed,
    )


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


def get_greek_bs_european(
    St: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    call: bool,
    greek: str,
    engine: str = "analytical",
    greek_engine: str = "analytical",
    fd_scheme: str = "central",
    h: float | None = None,
    n_paths: int | None = None,
    seed: int | None = None,
) -> float:
    """Compute a Greek of a European option under Black-Scholes.

    Args:
        St: Spot price of the underlying.
        K: Strike.
        T: Time to maturity in years.
        r: Continuously compounded risk-free rate.
        sigma: Annualized Black-Scholes volatility.
        call: True for call, False for put.
        greek: Greek name: ``"delta"``, ``"gamma"``, ``"vega"``, or ``"rho"``.
        engine: Pricing engine used by finite differences: ``"analytical"``
            or ``"mc"``.
        greek_engine: Greek method: ``"analytical"`` or ``"fd"``.
        fd_scheme: Finite-difference scheme for first-order Greeks.
        h: Optional additive bump size. If omitted, finite differences use
            ``1e-4 * St`` for delta/gamma and ``1e-4`` for vega/rho.
        n_paths: Number of Monte Carlo paths for finite differences over MC.
        seed: Monte Carlo seed for common random numbers.

    Returns:
        Requested Greek per unit change in its parameter.

    Raises:
        ValueError: If inputs or engine selectors violate the API contract.
    """
    _validate_greek_request(
        St=St,
        K=K,
        T=T,
        sigma=sigma,
        greek=greek,
        engine=engine,
        greek_engine=greek_engine,
        fd_scheme=fd_scheme,
        h=h,
        n_paths=n_paths,
        seed=seed,
    )
    contract = EuropeanOption(K=K, expiry=T, call=call)
    market = MarketData(
        spot=St,
        curve=FlatDiscountCurve(R=r, compounding="continuous"),
    )
    model = BlackScholesModel(sigma=sigma)

    if greek_engine == "analytical":
        return AnalyticalGreeks().greek(contract, model, market, greek)

    pricing_engine = _black_scholes_engine(engine, n_paths=n_paths, seed=seed)
    greek_calculator = FiniteDifferenceGreeks(
        pricing_engine=pricing_engine,
        fd_scheme=fd_scheme,
        h=h,
    )
    return greek_calculator.greek(contract, model, market, greek)


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


def _validate_cost_of_carry_request(
    St: float,
    K: float,
    T: float,
    sigma: float,
    engine: str,
    n_paths: int | None,
) -> None:
    if engine not in {"analytical", "mc"}:
        raise ValueError("engine must be 'analytical' or 'mc'.")
    if St <= 0:
        raise ValueError("Spot must be positive.")
    if K <= 0:
        raise ValueError("Strike must be positive.")
    if T < 0:
        raise ValueError("Time to maturity must be non-negative.")
    if sigma <= 0:
        raise ValueError("Volatility must be positive.")
    if engine == "mc" and (n_paths is None or n_paths <= 0):
        raise ValueError("n_paths must be positive when engine='mc'.")


def _validate_greek_request(
    St: float,
    K: float,
    T: float,
    sigma: float,
    greek: str,
    engine: str,
    greek_engine: str,
    fd_scheme: str,
    h: float | None,
    n_paths: int | None,
    seed: int | None,
) -> None:
    if greek not in {"delta", "gamma", "vega", "rho"}:
        raise ValueError("greek must be 'delta', 'gamma', 'vega', or 'rho'.")
    if engine not in {"analytical", "mc"}:
        raise ValueError("engine must be 'analytical' or 'mc'.")
    if greek_engine not in {"analytical", "fd"}:
        raise ValueError("greek_engine must be 'analytical' or 'fd'.")
    if St <= 0:
        raise ValueError("Spot must be positive.")
    if K <= 0:
        raise ValueError("Strike must be positive.")
    if T <= 0:
        raise ValueError("Time to maturity must be positive.")
    if sigma <= 0:
        raise ValueError("Volatility must be positive.")
    if greek_engine == "analytical":
        return
    if fd_scheme not in {"forward", "central"}:
        raise ValueError("fd_scheme must be 'forward' or 'central'.")
    if h is not None and h <= 0:
        raise ValueError("h must be positive.")
    if engine == "mc":
        if n_paths is None or n_paths <= 0:
            raise ValueError("n_paths must be positive when engine='mc'.")
        if seed is None:
            raise ValueError("seed is required when engine='mc'.")


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
