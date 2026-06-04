# hesperides/greeks/finite_difference.py

from dataclasses import dataclass

from hesperides.contracts.european import EuropeanOption
from hesperides.engines.base import Engine
from hesperides.greeks.bumps import bump_rate, bump_sigma, bump_spot
from hesperides.market.data import MarketData
from hesperides.models.black_scholes import BlackScholesModel
from hesperides.pricers.option_pricer import OptionPricer


@dataclass(frozen=True)
class FiniteDifferenceGreeks:
    """Finite-difference Greeks by bump-and-reprice."""

    pricing_engine: Engine
    fd_scheme: str = "central"
    h: float | None = None

    def greek(
        self,
        contract: EuropeanOption,
        model: BlackScholesModel,
        market: MarketData,
        greek: str,
    ) -> float:
        """Compute one Greek by bumping model or market inputs.

        Args:
            contract: European option contract.
            model: Black-Scholes model containing volatility.
            market: Market data containing spot and discount curve.
            greek: Greek name. Supported values are ``"delta"``,
                ``"gamma"``, ``"vega"``, and ``"rho"``.

        Returns:
            Requested finite-difference Greek.

        Raises:
            ValueError: If the contract, scheme, bump, or Greek is unsupported.
        """
        self._validate(contract, model, market)
        h = self._bump_size(greek, market)
        if greek == "gamma":
            return self._second_spot_derivative(contract, model, market, h)
        if greek in {"delta", "vega", "rho"}:
            return self._first_derivative(contract, model, market, greek, h)
        raise ValueError("greek must be 'delta', 'gamma', 'vega', or 'rho'.")

    def _first_derivative(
        self,
        contract: EuropeanOption,
        model: BlackScholesModel,
        market: MarketData,
        greek: str,
        h: float,
    ) -> float:
        if self.fd_scheme == "forward":
            up_model, up_market = self._bumped(model, market, greek, h)
            up = self._price(contract, up_model, up_market)
            base = self._price(contract, model, market)
            return (up - base) / h

        up_model, up_market = self._bumped(model, market, greek, h)
        down_model, down_market = self._bumped(model, market, greek, -h)
        up = self._price(contract, up_model, up_market)
        down = self._price(contract, down_model, down_market)
        return (up - down) / (2.0 * h)

    def _second_spot_derivative(
        self,
        contract: EuropeanOption,
        model: BlackScholesModel,
        market: MarketData,
        h: float,
    ) -> float:
        up_market = bump_spot(market, h)
        down_market = bump_spot(market, -h)
        up = self._price(contract, model, up_market)
        base = self._price(contract, model, market)
        down = self._price(contract, model, down_market)
        return (up - 2.0 * base + down) / (h * h)

    def _price(
        self,
        contract: EuropeanOption,
        model: BlackScholesModel,
        market: MarketData,
    ) -> float:
        return OptionPricer(contract, model, market, self.pricing_engine).price()

    @staticmethod
    def _bumped(
        model: BlackScholesModel,
        market: MarketData,
        greek: str,
        h: float,
    ) -> tuple[BlackScholesModel, MarketData]:
        if greek == "delta":
            return model, bump_spot(market, h)
        if greek == "vega":
            return bump_sigma(model, h), market
        if greek == "rho":
            return model, bump_rate(market, h)
        raise ValueError("Only first-order Greeks can be bumped here.")

    def _bump_size(self, greek: str, market: MarketData) -> float:
        if self.h is not None:
            return self.h
        if greek in {"delta", "gamma"}:
            return 1e-4 * market.spot
        if greek in {"vega", "rho"}:
            return 1e-4
        raise ValueError("greek must be 'delta', 'gamma', 'vega', or 'rho'.")

    def _validate(
        self,
        contract: EuropeanOption,
        model: BlackScholesModel,
        market: MarketData,
    ) -> None:
        if not isinstance(contract, EuropeanOption):
            raise ValueError("Finite-difference Greeks require a European option.")
        if self.fd_scheme not in {"forward", "central"}:
            raise ValueError("fd_scheme must be 'forward' or 'central'.")
        if self.h is not None and self.h <= 0:
            raise ValueError("h must be positive.")
        if market.spot <= 0:
            raise ValueError("Spot must be positive.")
        if contract.K <= 0:
            raise ValueError("Strike must be positive.")
        if contract.expiry <= 0:
            raise ValueError("Time to maturity must be positive.")
        if model.sigma <= 0:
            raise ValueError("Volatility must be positive.")
