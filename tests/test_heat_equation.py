import math

import numpy as np
from numpy.testing import assert_allclose
import pytest

import derivatives_pricing.api as pricing


def _sine_solution(x, kappa, M, T):
    decay = math.exp(-kappa * (math.pi / M) ** 2 * T)
    return decay * np.sin(math.pi * x / M)


@pytest.mark.parametrize(
    "scheme, n_x, n_t",
    [
        ("explicit", 40, 400),
        ("implicit", 40, 40),
    ],
)
def test_heat_sine_solution(scheme, n_x, n_t):
    kappa = 0.5
    M = 1.0
    T = 0.02

    x_grid, u_T = pricing.solve_heat_equation(
        lambda x: np.sin(math.pi * x / M),
        kappa=kappa,
        M=M,
        T=T,
        n_x=n_x,
        n_t=n_t,
        scheme=scheme,
    )

    expected = _sine_solution(x_grid, kappa, M, T)
    assert_allclose(u_T, expected, atol=1e-3)


def test_explicit_stability_threshold():
    kappa = 1.0
    M = 1.0
    n_x = 50
    dx = M / n_x
    T = 0.01

    def alternating_mode(x):
        values = np.zeros_like(x)
        values[1:-1] = (-1.0) ** np.arange(1, len(x) - 1)
        return values

    stable_ratio = 0.5
    stable_dt = stable_ratio * dx**2 / kappa
    stable_n_t = round(T / stable_dt)
    stable_T = stable_n_t * stable_dt
    _, stable = pricing.solve_heat_equation(
        alternating_mode,
        kappa=kappa,
        M=M,
        T=stable_T,
        n_x=n_x,
        n_t=stable_n_t,
        scheme="explicit",
    )

    unstable_ratio = 0.8
    unstable_dt = unstable_ratio * dx**2 / kappa
    unstable_n_t = round(T / unstable_dt)
    unstable_T = unstable_n_t * unstable_dt
    _, unstable = pricing.solve_heat_equation(
        alternating_mode,
        kappa=kappa,
        M=M,
        T=unstable_T,
        n_x=n_x,
        n_t=unstable_n_t,
        scheme="explicit",
    )

    assert np.max(np.abs(stable)) <= 1.0
    assert np.max(np.abs(unstable)) > 1e3


def test_explicit_convergence():
    kappa = 0.5
    M = 1.0
    T = 0.02

    coarse_x, coarse = pricing.solve_heat_equation(
        lambda x: np.sin(math.pi * x / M),
        kappa=kappa,
        M=M,
        T=T,
        n_x=20,
        n_t=200,
        scheme="explicit",
    )
    fine_x, fine = pricing.solve_heat_equation(
        lambda x: np.sin(math.pi * x / M),
        kappa=kappa,
        M=M,
        T=T,
        n_x=40,
        n_t=800,
        scheme="explicit",
    )

    coarse_error = np.max(np.abs(coarse - _sine_solution(coarse_x, kappa, M, T)))
    fine_error = np.max(np.abs(fine - _sine_solution(fine_x, kappa, M, T)))

    assert fine_error < 0.35 * coarse_error


def test_implicit_stability_large_time_step():
    kappa = 0.5
    M = 1.0
    T = 0.02
    n_x = 40
    n_t = 4

    x_grid, u_T = pricing.solve_heat_equation(
        lambda x: np.sin(math.pi * x / M),
        kappa=kappa,
        M=M,
        T=T,
        n_x=n_x,
        n_t=n_t,
        scheme="implicit",
    )

    expected = _sine_solution(x_grid, kappa, M, T)
    assert_allclose(u_T, expected, atol=2e-3)


@pytest.mark.parametrize("call", [True, False])
@pytest.mark.parametrize(
    "params",
    [
        dict(St=100.0, K=100.0, T=1.0, r=0.03, sigma=0.20),
        dict(St=100.0, K=90.0, T=0.5, r=0.01, sigma=0.25),
        dict(St=100.0, K=110.0, T=1.5, r=0.04, sigma=0.30),
    ],
)
def test_black_scholes_heat_matches_closed_form(call, params):
    closed_form = pricing.get_price_bs_european(**params, call=call)
    heat = pricing.get_price_bs_european_heat(**params, call=call)

    assert heat == pytest.approx(closed_form, abs=5e-3)


@pytest.mark.parametrize(
    "kwargs, message",
    [
        (dict(initial_condition=1.0), "initial_condition"),
        (dict(scheme="crank"), "scheme"),
        (dict(boundary_type="robin"), "boundary_type"),
        (dict(kappa=0.0), "kappa"),
        (dict(M=0.0), "M"),
        (dict(T=0.0), "T"),
        (dict(n_x=0), "n_x"),
        (dict(n_t=0), "n_t"),
    ],
)
def test_heat_solver_validation(kwargs, message):
    params = dict(
        initial_condition=lambda x: np.sin(math.pi * x),
        kappa=0.5,
        M=1.0,
        T=0.01,
        n_x=10,
        n_t=10,
    )
    params.update(kwargs)

    with pytest.raises(ValueError, match=message):
        pricing.solve_heat_equation(**params)


@pytest.mark.parametrize(
    "kwargs, message",
    [
        (dict(St=0.0), "Spot"),
        (dict(K=0.0), "Strike"),
        (dict(T=0.0), "Time"),
        (dict(sigma=0.0), "Volatility"),
        (dict(n_x=0), "n_x"),
        (dict(n_t=0), "n_t"),
        (dict(scheme="crank"), "scheme"),
    ],
)
def test_black_scholes_heat_validation(kwargs, message):
    params = dict(St=100.0, K=100.0, T=1.0, r=0.03, sigma=0.20, call=True)
    params.update(kwargs)

    with pytest.raises(ValueError, match=message):
        pricing.get_price_bs_european_heat(**params)
