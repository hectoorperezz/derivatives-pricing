# hesperides/engines/bs_analytical_engine.py

import math

from hesperides.contracts.asian import GeometricAsianOption
from hesperides.contracts.base import Option
from hesperides.contracts.european import EuropeanOption
from hesperides.engines.base import Engine
from hesperides.market.data import MarketData
from hesperides.models.black_scholes import BlackScholesModel


class BlackScholesAnalyticalEngine(Engine):
    """Closed-form Black-Scholes pricing for supported contracts."""

    def price(
        self, contract: Option, model: BlackScholesModel, market: MarketData
    ) -> float:
        """Compute a closed-form Black-Scholes price."""
        self._validate_market_contract(contract, model, market)
        if isinstance(contract, EuropeanOption):
            return self._price_european(contract, model, market)
        if isinstance(contract, GeometricAsianOption):
            return self._price_geometric_asian(contract, model, market)
        raise ValueError(f"Unsupported contract type: {type(contract).__name__}.")

    def _price_european(
        self,
        contract: EuropeanOption,
        model: BlackScholesModel,
        market: MarketData,
    ) -> float:
        S = market.spot
        K = contract.K
        T = contract.expiry
        r = market.curve.rate(T)
        sigma = model.sigma

        if T == 0:
            return self._intrinsic_value(S, K, contract.call)

        sqrt_t = math.sqrt(T)
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt_t)
        d2 = d1 - sigma * sqrt_t
        discount = market.curve.discount_factor(T)

        if contract.call:
            return S * _norm_cdf(d1) - K * discount * _norm_cdf(d2)
        return K * discount * _norm_cdf(-d2) - S * _norm_cdf(-d1)

    def _price_geometric_asian(
        self,
        contract: GeometricAsianOption,
        model: BlackScholesModel,
        market: MarketData,
    ) -> float:
        S = market.spot
        K = contract.K
        T = contract.expiry
        r = market.curve.rate(T)
        sigma = model.sigma

        if T == 0:
            return self._intrinsic_value(S, K, contract.call)

        mean = math.log(S) + (r - 0.5 * sigma**2) * T / 2.0
        variance = sigma**2 * T / 3.0
        std = math.sqrt(variance)
        d1 = (mean - math.log(K) + variance) / std
        d2 = d1 - std
        expected_average = math.exp(mean + 0.5 * variance)
        discount = market.curve.discount_factor(T)

        if contract.call:
            return discount * (expected_average * _norm_cdf(d1) - K * _norm_cdf(d2))
        return discount * (K * _norm_cdf(-d2) - expected_average * _norm_cdf(-d1))

    @staticmethod
    def _validate_market_contract(
        contract: Option,
        model: BlackScholesModel,
        market: MarketData,
    ) -> None:
        T = getattr(contract, "expiry", None)
        K = getattr(contract, "K", None)
        if market.spot <= 0:
            raise ValueError("Spot must be positive.")
        if K is None or K <= 0:
            raise ValueError("Strike must be positive.")
        if T is None or T < 0:
            raise ValueError("Time to maturity must be non-negative.")
        if T > 0 and model.sigma <= 0:
            raise ValueError("Volatility must be positive.")

    @staticmethod
    def _intrinsic_value(S: float, K: float, call: bool) -> float:
        return float(max(S - K, 0.0) if call else max(K - S, 0.0))


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
