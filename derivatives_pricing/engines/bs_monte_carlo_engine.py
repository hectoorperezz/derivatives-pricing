# derivatives_pricing/engines/bs_monte_carlo_engine.py

from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

from derivatives_pricing.contracts.asian import GeometricAsianOption
from derivatives_pricing.contracts.base import Option
from derivatives_pricing.contracts.european import EuropeanOption
from derivatives_pricing.engines.base import Engine
from derivatives_pricing.market.data import MarketData
from derivatives_pricing.models.black_scholes import BlackScholesModel


@dataclass(frozen=True)
class BlackScholesMonteCarloEngine(Engine):
    """Monte Carlo Black-Scholes pricing using exact GBM simulation."""

    n_paths: int
    n_steps: int | None = None
    seed: int | None = None

    def price(
        self, contract: Option, model: BlackScholesModel, market: MarketData
    ) -> float:
        """Estimate a Black-Scholes price by averaging discounted payoffs."""
        self._validate(contract, model, market)
        if isinstance(contract, EuropeanOption):
            terminal = self._simulate_terminal_spots(
                model=model,
                market=market,
                T=contract.expiry,
            )
            payoffs = contract.payoff(terminal)
        elif isinstance(contract, GeometricAsianOption):
            paths = self._simulate_paths(
                model=model,
                market=market,
                T=contract.expiry,
                n_steps=self.n_steps_or_raise(),
            )
            averages = np.exp(np.mean(np.log(paths), axis=1))
            payoffs = contract.payoff(averages)
        else:
            raise ValueError(f"Unsupported contract type: {type(contract).__name__}.")

        return float(market.curve.discount_factor(contract.expiry) * np.mean(payoffs))

    def n_steps_or_raise(self) -> int:
        """Return n_steps, or fail for path-dependent contracts."""
        if self.n_steps is None:
            raise ValueError("n_steps is required for geometric Asian Monte Carlo.")
        return self.n_steps

    def _validate(
        self,
        contract: Option,
        model: BlackScholesModel,
        market: MarketData,
    ) -> None:
        T = getattr(contract, "expiry", None)
        K = getattr(contract, "K", None)
        if self.n_paths <= 0:
            raise ValueError("n_paths must be positive.")
        if isinstance(contract, GeometricAsianOption) and self.n_steps_or_raise() <= 0:
            raise ValueError("n_steps must be positive.")
        if market.spot <= 0:
            raise ValueError("Spot must be positive.")
        if model.sigma <= 0:
            raise ValueError("Volatility must be positive.")
        if K is None or K <= 0:
            raise ValueError("Strike must be positive.")
        if T is None or T < 0:
            raise ValueError("Time to maturity must be non-negative.")

    def _simulate_terminal_spots(
        self,
        model: BlackScholesModel,
        market: MarketData,
        T: float,
    ) -> NDArray[np.float64]:
        """Simulate terminal spots exactly under Black-Scholes."""
        sigma = model.sigma
        r = market.curve.rate(T)
        carry = model.cost_of_carry(r)
        rng = np.random.default_rng(self.seed)
        z = rng.standard_normal(self.n_paths)
        drift = (carry - 0.5 * sigma**2) * T
        diffusion = sigma * np.sqrt(T) * z
        return market.spot * np.exp(drift + diffusion)

    def _simulate_paths(
        self,
        model: BlackScholesModel,
        market: MarketData,
        T: float,
        n_steps: int,
    ) -> NDArray[np.float64]:
        """Simulate exact GBM spots on a uniform grid excluding the initial spot."""
        sigma = model.sigma
        r = market.curve.rate(T)
        carry = model.cost_of_carry(r)
        dt = T / n_steps
        rng = np.random.default_rng(self.seed)
        z = rng.standard_normal((self.n_paths, n_steps))
        log_returns = (carry - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
        log_paths = np.log(market.spot) + np.cumsum(log_returns, axis=1)
        return np.exp(log_paths)
