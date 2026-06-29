# derivatives_pricing/api.py

__all__ = [
    "get_price_binomial_european",
    "get_price_bs_european",
    "get_price_bs_european_dividend",
    "get_price_fx_option",
    "get_price_future_option",
    "get_price_bs_geometric_asian",
    "solve_heat_equation",
    "get_price_bs_european_heat",
    "get_greek_bs_european",
    "compute_static_arbitrage_quantity",
]

import math

import numpy as np

from derivatives_pricing.contracts.asian import GeometricAsianOption
from derivatives_pricing.contracts.european import EuropeanOption
from derivatives_pricing.contracts.initial_condition import InitialCondition
from derivatives_pricing.engines.bs_analytical_engine import BlackScholesAnalyticalEngine
from derivatives_pricing.engines.bs_monte_carlo_engine import BlackScholesMonteCarloEngine
from derivatives_pricing.engines.heat_equation_engine import HeatEquationEngine
from derivatives_pricing.greeks.analytical import AnalyticalGreeks
from derivatives_pricing.greeks.finite_difference import FiniteDifferenceGreeks
from derivatives_pricing.market.call_surface import CallSurface
from derivatives_pricing.market.curves import FlatDiscountCurve
from derivatives_pricing.market.data import MarketData
from derivatives_pricing.models.black_scholes import BlackScholesModel
from derivatives_pricing.models.heat_equation import HeatEquationModel
from derivatives_pricing.models.binomial import BinomialModel
from derivatives_pricing.engines.binomial_engine import BinomialTreeEngine
from derivatives_pricing.pricers.option_pricer import OptionPricer


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


def solve_heat_equation(
    initial_condition,
    kappa: float,
    M: float,
    T: float,
    n_x: int,
    n_t: int,
    scheme: str = "explicit",
    left_boundary=0.0,
    right_boundary=0.0,
    boundary_type: str = "dirichlet",
):
    """Solve the one-dimensional heat equation by finite differences.

    Args:
        initial_condition: Callable mapping the spatial grid to initial values.
        kappa: Diffusion coefficient in ``v_t = kappa * v_xx``.
        M: Right endpoint of the spatial domain ``[0, M]``.
        T: Final time.
        n_x: Number of spatial intervals.
        n_t: Number of time steps.
        scheme: Time-stepping scheme: ``"explicit"`` or ``"implicit"``.
        left_boundary: Left boundary value or slope.
        right_boundary: Right boundary value or slope.
        boundary_type: Boundary convention: ``"dirichlet"`` or ``"neumann"``.

    Returns:
        Tuple ``(x_grid, u_T)`` with the spatial grid and final solution.
    """
    _validate_heat_request(
        initial_condition=initial_condition,
        kappa=kappa,
        M=M,
        T=T,
        n_x=n_x,
        n_t=n_t,
        scheme=scheme,
        boundary_type=boundary_type,
    )
    condition = InitialCondition(initial_condition)
    model = HeatEquationModel(
        kappa=kappa,
        M=M,
        T=T,
        left_boundary=left_boundary,
        right_boundary=right_boundary,
        boundary_type=boundary_type,
    )
    engine = HeatEquationEngine(n_x=n_x, n_t=n_t, scheme=scheme)
    return engine.solve(condition, model)


def get_price_bs_european_heat(
    St: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    call: bool,
    n_x: int = 400,
    n_t: int = 400,
    scheme: str = "implicit",
) -> float:
    """Price a European option through the heat-equation transform.

    Args:
        St: Spot price of the underlying.
        K: Strike.
        T: Time to maturity in years.
        r: Continuously compounded risk-free rate.
        sigma: Annualized Black-Scholes volatility.
        call: True for call, False for put.
        n_x: Number of heat-equation spatial intervals.
        n_t: Number of heat-equation time steps.
        scheme: Heat-equation scheme: ``"explicit"`` or ``"implicit"``.

    Returns:
        European option price at valuation date.
    """
    _validate_black_scholes_heat_request(
        St=St,
        K=K,
        T=T,
        sigma=sigma,
        n_x=n_x,
        n_t=n_t,
        scheme=scheme,
    )
    y_min, y_max, y0 = _black_scholes_heat_domain(
        St=St,
        K=K,
        T=T,
        r=r,
        sigma=sigma,
    )
    M = y_max - y_min
    initial_condition = _black_scholes_heat_initial_condition(
        K=K,
        sigma=sigma,
        call=call,
        y_min=y_min,
    )
    left_boundary, right_boundary = _black_scholes_heat_boundaries(
        K=K,
        sigma=sigma,
        call=call,
        y_min=y_min,
        y_max=y_max,
    )
    z_grid, G_T = solve_heat_equation(
        initial_condition=initial_condition,
        kappa=0.5,
        M=M,
        T=T,
        n_x=n_x,
        n_t=n_t,
        scheme=scheme,
        left_boundary=left_boundary,
        right_boundary=right_boundary,
        boundary_type="dirichlet",
    )
    z0 = y0 - y_min
    G_value = float(np.interp(z0, z_grid, G_T))
    return math.exp(-r * T) * G_value


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


def _validate_heat_request(
    initial_condition,
    kappa: float,
    M: float,
    T: float,
    n_x: int,
    n_t: int,
    scheme: str,
    boundary_type: str,
) -> None:
    if not callable(initial_condition):
        raise ValueError("initial_condition must be callable.")
    if scheme not in {"explicit", "implicit"}:
        raise ValueError("scheme must be 'explicit' or 'implicit'.")
    if boundary_type not in {"dirichlet", "neumann"}:
        raise ValueError("boundary_type must be 'dirichlet' or 'neumann'.")
    if kappa <= 0:
        raise ValueError("kappa must be positive.")
    if M <= 0:
        raise ValueError("M must be positive.")
    if T <= 0:
        raise ValueError("T must be positive.")
    if n_x < 1:
        raise ValueError("n_x must be at least 1.")
    if n_t < 1:
        raise ValueError("n_t must be at least 1.")


def _validate_black_scholes_heat_request(
    St: float,
    K: float,
    T: float,
    sigma: float,
    n_x: int,
    n_t: int,
    scheme: str,
) -> None:
    if St <= 0:
        raise ValueError("Spot must be positive.")
    if K <= 0:
        raise ValueError("Strike must be positive.")
    if T <= 0:
        raise ValueError("Time to maturity must be positive.")
    if sigma <= 0:
        raise ValueError("Volatility must be positive.")
    if n_x < 1:
        raise ValueError("n_x must be at least 1.")
    if n_t < 1:
        raise ValueError("n_t must be at least 1.")
    if scheme not in {"explicit", "implicit"}:
        raise ValueError("scheme must be 'explicit' or 'implicit'.")


def _black_scholes_heat_domain(
    St: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
) -> tuple[float, float, float]:
    y0 = (math.log(St) - (0.5 * sigma**2 - r) * T) / sigma
    y_strike = math.log(K) / sigma
    margin = 8.0 * math.sqrt(T)
    y_min = min(y0, y_strike) - margin
    y_max = max(y0, y_strike) + margin
    return y_min, y_max, y0


def _black_scholes_heat_initial_condition(
    K: float,
    sigma: float,
    call: bool,
    y_min: float,
):
    def initial_condition(z_grid: np.ndarray) -> np.ndarray:
        y_grid = y_min + z_grid
        underlying = np.exp(sigma * y_grid)
        if call:
            return np.maximum(underlying - K, 0.0)
        return np.maximum(K - underlying, 0.0)

    return initial_condition


def _black_scholes_heat_boundaries(
    K: float,
    sigma: float,
    call: bool,
    y_min: float,
    y_max: float,
):
    if call:

        def left_boundary(t: float) -> float:
            return 0.0

        def right_boundary(t: float) -> float:
            return math.exp(sigma * y_max + 0.5 * sigma**2 * t) - K

    else:

        def left_boundary(t: float) -> float:
            return K - math.exp(sigma * y_min + 0.5 * sigma**2 * t)

        def right_boundary(t: float) -> float:
            return 0.0

    return left_boundary, right_boundary


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
