# hesperides/greeks/analytical.py

import math

from hesperides.contracts.european import EuropeanOption
from hesperides.market.data import MarketData
from hesperides.models.black_scholes import BlackScholesModel
from hesperides.utils.black_scholes import d1_d2
from hesperides.utils.normal import normal_cdf, normal_pdf


class AnalyticalGreeks:
    """Closed-form Black-Scholes Greeks for European options."""

    def greek(
        self,
        contract: EuropeanOption,
        model: BlackScholesModel,
        market: MarketData,
        greek: str,
    ) -> float:
        """Compute one closed-form Greek.

        Args:
            contract: European option contract.
            model: Black-Scholes model containing volatility.
            market: Market data containing spot and discount curve.
            greek: Greek name. Supported values are ``"delta"``,
                ``"gamma"``, ``"vega"``, and ``"rho"``.

        Returns:
            Requested Greek per unit change in the underlying parameter.

        Raises:
            ValueError: If the contract, market, model, or Greek is unsupported.
        """
        self._validate(contract, model, market)
        d1, d2 = self._d1_d2(contract, model, market)
        if greek == "delta":
            return self._delta(contract, d1)
        if greek == "gamma":
            return self._gamma(contract, model, market, d1)
        if greek == "vega":
            return self._vega(contract, market, d1)
        if greek == "rho":
            return self._rho(contract, market, d2)
        raise ValueError("greek must be 'delta', 'gamma', 'vega', or 'rho'.")

    @staticmethod
    def _validate(
        contract: EuropeanOption,
        model: BlackScholesModel,
        market: MarketData,
    ) -> None:
        if not isinstance(contract, EuropeanOption):
            raise ValueError("Analytical Greeks require a European option.")
        if market.spot <= 0:
            raise ValueError("Spot must be positive.")
        if contract.K <= 0:
            raise ValueError("Strike must be positive.")
        if contract.expiry <= 0:
            raise ValueError("Time to maturity must be positive.")
        if model.sigma <= 0:
            raise ValueError("Volatility must be positive.")

    @staticmethod
    def _d1_d2(
        contract: EuropeanOption,
        model: BlackScholesModel,
        market: MarketData,
    ) -> tuple[float, float]:
        return d1_d2(
            S=market.spot,
            K=contract.K,
            T=contract.expiry,
            r=market.curve.rate(contract.expiry),
            sigma=model.sigma,
        )

    @staticmethod
    def _delta(contract: EuropeanOption, d1: float) -> float:
        if contract.call:
            return normal_cdf(d1)
        return normal_cdf(d1) - 1.0

    @staticmethod
    def _gamma(
        contract: EuropeanOption,
        model: BlackScholesModel,
        market: MarketData,
        d1: float,
    ) -> float:
        return normal_pdf(d1) / (market.spot * model.sigma * math.sqrt(contract.expiry))

    @staticmethod
    def _vega(contract: EuropeanOption, market: MarketData, d1: float) -> float:
        return market.spot * normal_pdf(d1) * math.sqrt(contract.expiry)

    @staticmethod
    def _rho(contract: EuropeanOption, market: MarketData, d2: float) -> float:
        K = contract.K
        T = contract.expiry
        discount = market.curve.discount_factor(T)
        if contract.call:
            return K * T * discount * normal_cdf(d2)
        return -K * T * discount * normal_cdf(-d2)
