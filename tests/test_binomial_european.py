"""Regression tests for binomial pricing of European options."""
from fractions import Fraction

import numpy as np
import pytest

import derivatives_pricing.api as pricing




@pytest.mark.regression
def test_european_put_pathwise_regression():
    """European put regression scenario: S0=100, u=1.25, d=0.85."""
    S0, K, T = 100.0, 110.0, 4
    R, u, d = 0.05, 1.25, 0.85

    # Fixed path of ups/downs in the reference tree.
    path_ups = np.array([0, 1, 0, 1], dtype=bool)
    factors = np.where(path_ups, u, d)
    spots = np.concatenate([[S0], S0 * np.cumprod(factors)])

    expected = [
        Fraction(1_089_925, 111_132),
        Fraction(315_005, 18_522),
        Fraction(17_725, 2_352),
        Fraction(3_545, 224),
        Fraction(0, 1),
    ]

    prices = []
    for eval_date in range(T + 1):
        price = pricing.get_price_binomial_european(
            spots[eval_date], K, T - eval_date, R, u, d, call=False
        )
        if not isinstance(price, (float, np.floating)):
            raise TypeError(
                "get_price_binomial_european must return a float. "
                f"Got {type(price).__name__}."
            )
        prices.append(float(price))

    np.testing.assert_allclose(
        prices,
        [float(x) for x in expected],
        atol=2.0,
        rtol=0.0,
    )
