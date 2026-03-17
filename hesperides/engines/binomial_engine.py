# hesperides/engines/binomial_engine.py

import math
import numpy as np

from hesperides.engines.base import Engine
from hesperides.contracts.european import EuropeanOption
from hesperides.market.curves import FlatDiscountCurve
from hesperides.models.binomial import BinomialModel


class AnalyticBinomialEngine(Engine):
    """Analytical binomial pricing. Valid for European options only."""

    def price(self, contract: EuropeanOption, model: BinomialModel,
              curve: FlatDiscountCurve, St: float) -> float:
        """Price a European option via risk-neutral expectation."""
        T = contract.expiry
        q = model.risk_neutral_prob(curve, 0)

        j = np.arange(T + 1, dtype=np.float64)
        S_T = St * model.u ** j * model.d ** (T - j)
        payoffs = contract.payoff(S_T)

        coeffs = np.array([math.comb(T, int(ji)) for ji in j], dtype=np.float64)
        weights = coeffs * q ** j * (1 - q) ** (T - j)

        return float(np.sum(weights * payoffs) * curve.discount_factor(T))