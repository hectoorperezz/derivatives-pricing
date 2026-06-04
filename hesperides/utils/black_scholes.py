# hesperides/utils/black_scholes.py

import math


def d1_d2(S: float, K: float, T: float, r: float, sigma: float) -> tuple[float, float]:
    """Compute the Black-Scholes ``d1`` and ``d2`` terms.

    Args:
        S: Spot price.
        K: Strike.
        T: Time to maturity.
        r: Continuously compounded risk-free rate.
        sigma: Black-Scholes volatility.

    Returns:
        Pair ``(d1, d2)``.
    """
    sqrt_t = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t
    return d1, d2
