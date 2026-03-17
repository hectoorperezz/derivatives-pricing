"""
Additional tests for Assignment 1: Binomial pricing of European options.

Tests cover:
- All intermediate tree nodes from Exercise 3 (T=4 put scenario).
- Put-call parity (algebraic invariant, no manual values needed).
- Edge cases: deep in/out-of-the-money, T=1 single period.
"""

import numpy as np
import pytest

import hesperides.api as hapi

# ---------------------------------------------------------------------------
# Shared scenario from Exercise 3
# S0=100, u=1.25, d=0.85, R=0.05, T=4, K=110  (European put)
# ---------------------------------------------------------------------------
S0, K, T = 100.0, 110.0, 4
R, u, d = 0.05, 1.25, 0.85


# ---------------------------------------------------------------------------
# 1. Intermediate tree nodes (all nodos computed by backward induction)
# ---------------------------------------------------------------------------

class TestTreeNodes:
    """Verify that get_price_binomial_european matches the backward-induction
    values calculated manually in Exercise 3."""

    # t=3 nodes
    def test_t3_node_195(self):
        price = hapi.get_price_binomial_european(195.3125, K, 1, R, u, d, call=False)
        np.testing.assert_allclose(price, 0.0, atol=1e-4)

    def test_t3_node_132(self):
        price = hapi.get_price_binomial_european(132.8125, K, 1, R, u, d, call=False)
        np.testing.assert_allclose(price, 0.0, atol=1e-4)

    def test_t3_node_90(self):
        price = hapi.get_price_binomial_european(90.3125, K, 1, R, u, d, call=False)
        np.testing.assert_allclose(price, 15.8259, atol=1e-3)

    def test_t3_node_61(self):
        price = hapi.get_price_binomial_european(61.4125, K, 1, R, u, d, call=False)
        np.testing.assert_allclose(price, 43.3494, atol=1e-3)

    # t=2 nodes
    def test_t2_node_156(self):
        price = hapi.get_price_binomial_european(156.25, K, 2, R, u, d, call=False)
        np.testing.assert_allclose(price, 0.0, atol=1e-4)

    def test_t2_node_106(self):
        price = hapi.get_price_binomial_european(106.25, K, 2, R, u, d, call=False)
        np.testing.assert_allclose(price, 7.5361, atol=1e-3)

    def test_t2_node_72(self):
        price = hapi.get_price_binomial_european(72.25, K, 2, R, u, d, call=False)
        np.testing.assert_allclose(price, 28.1787, atol=1e-3)

    # t=1 nodes
    def test_t1_node_125(self):
        price = hapi.get_price_binomial_european(125.0, K, 3, R, u, d, call=False)
        np.testing.assert_allclose(price, 3.5886, atol=1e-3)

    def test_t1_node_85(self):
        price = hapi.get_price_binomial_european(85.0, K, 3, R, u, d, call=False)
        np.testing.assert_allclose(price, 17.0071, atol=1e-3)

    # t=0
    def test_t0_root(self):
        price = hapi.get_price_binomial_european(S0, K, T, R, u, d, call=False)
        np.testing.assert_allclose(price, 9.8075, atol=1e-3)


# ---------------------------------------------------------------------------
# 2. Put-call parity: C - P = S0 - K / (1+R)^T
# Holds exactly in the binomial model for any valid set of parameters.
# ---------------------------------------------------------------------------

class TestPutCallParity:

    @pytest.mark.parametrize("St, K_, T_", [
        (100.0, 110.0, 4),
        (100.0, 100.0, 4),
        (100.0,  90.0, 4),
        (125.0, 110.0, 3),
        ( 85.0, 110.0, 3),
        (100.0, 110.0, 1),
    ])
    def test_parity(self, St, K_, T_):
        call = hapi.get_price_binomial_european(St, K_, T_, R, u, d, call=True)
        put  = hapi.get_price_binomial_european(St, K_, T_, R, u, d, call=False)
        lhs = call - put
        rhs = St - K_ / (1 + R) ** T_
        np.testing.assert_allclose(lhs, rhs, atol=1e-6,
            err_msg=f"Put-call parity failed for St={St}, K={K_}, T={T_}")


# ---------------------------------------------------------------------------
# 3. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_T1_put_in_the_money(self):
        """T=1, put deep in the money: price = (K - S*d)*qd / (1+R)."""
        St, K_, T_ = 100.0, 110.0, 1
        qd = (u - (1 + R)) / (u - d)
        expected = (K_ - St * d) * qd / (1 + R)
        price = hapi.get_price_binomial_european(St, K_, T_, R, u, d, call=False)
        np.testing.assert_allclose(price, expected, atol=1e-10)

    def test_T1_call_out_of_the_money(self):
        """T=1, call deep out of the money: only the up-move pays off."""
        St, K_, T_ = 100.0, 110.0, 1
        qu = ((1 + R) - d) / (u - d)
        expected = (St * u - K_) * qu / (1 + R)
        price = hapi.get_price_binomial_european(St, K_, T_, R, u, d, call=True)
        np.testing.assert_allclose(price, expected, atol=1e-10)

    def test_call_and_put_nonnegative(self):
        """Option prices must always be >= 0."""
        for call in [True, False]:
            price = hapi.get_price_binomial_european(S0, K, T, R, u, d, call=call)
            assert price >= 0.0, f"Negative price for call={call}: {price}"

    def test_put_deep_itm_upper_bound(self):
        """Put price cannot exceed discounted strike."""
        price = hapi.get_price_binomial_european(1.0, K, T, R, u, d, call=False)
        assert price <= K / (1 + R) ** T + 1e-9
