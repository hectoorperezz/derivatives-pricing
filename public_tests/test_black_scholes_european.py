import math

import pytest

import hesperides.api as hapi


def test_european_parity():
    S, K, T, r, sigma = 100.0, 105.0, 2.0, 0.03, 0.25

    call = hapi.get_price_bs_european(S, K, T, r, sigma, call=True)
    put = hapi.get_price_bs_european(S, K, T, r, sigma, call=False)

    assert call - put == pytest.approx(S - K * math.exp(-r * T), abs=1e-12)
