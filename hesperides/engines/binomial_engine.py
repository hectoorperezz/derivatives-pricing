# hesperides/engines/binomial_engine.py

import numpy as np

from hesperides.engines.base import Engine
from hesperides.contracts.european import EuropeanOption
from hesperides.market.data import MarketData
from hesperides.models.binomial import BinomialModel


class BinomialTreeEngine(Engine):
    """Binomial tree pricing by backward induction. Valid for European options."""

    def price(self, contract: EuropeanOption, model: BinomialModel,
              market: MarketData) -> float:
        """Price a European option by backward induction on the binomial tree."""
        T = contract.expiry
        q = model.risk_neutral_prob(market.curve, 0)
        discount = 1.0 / (1.0 + market.curve.rate(0))

        # Terminal node values
        j = np.arange(T + 1, dtype=np.float64)
        S_T = market.spot * model.u ** j * model.d ** (T - j)
        V = contract.payoff(S_T)

        # Backward induction: T steps back, node dimension shrinks by 1 each step
        for _ in range(T):
            V = discount * (q * V[1:] + (1.0 - q) * V[:-1])

        return float(V[0])
