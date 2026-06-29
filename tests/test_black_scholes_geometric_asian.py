import math

import pytest

import derivatives_pricing.api as pricing


def test_asian_parity():
    S, K, T, r, sigma = 100.0, 105.0, 2.0, 0.03, 0.25

    call = pricing.get_price_bs_geometric_asian(S, K, T, r, sigma, call=True)
    put = pricing.get_price_bs_geometric_asian(S, K, T, r, sigma, call=False)

    expected_average = S * math.exp(r * T / 2.0 - sigma**2 * T / 12.0)
    expected_parity = math.exp(-r * T) * (expected_average - K)

    assert call - put == pytest.approx(expected_parity, abs=1e-12)
