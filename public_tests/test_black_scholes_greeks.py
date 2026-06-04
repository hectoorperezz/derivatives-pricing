import math

import pytest

import hesperides.api as hapi


QUANTLIB_PARAMS = dict(
    St=100.0,
    K=105.0,
    T=1.0,
    r=0.03,
    sigma=0.25,
)


@pytest.mark.parametrize(
    "call, greek, expected",
    [
        (True, "delta", 0.519874792906046),
        (True, "gamma", 0.015937884383973),
        (True, "vega", 39.844710959932094),
        (True, "rho", 42.865679832880510),
        (False, "delta", -0.480125207093954),
        (False, "gamma", 0.015937884383973),
        (False, "vega", 39.844710959932094),
        (False, "rho", -59.031101189712828),
    ],
)
def test_greeks_reference(call, greek, expected):
    # Reference values generated offline with QuantLib 1.42.1.
    # QuantLib is not a project dependency.
    value = hapi.get_greek_bs_european(
        **QUANTLIB_PARAMS,
        call=call,
        greek=greek,
    )

    assert value == pytest.approx(expected, abs=1e-8)


@pytest.mark.parametrize("call", [True, False])
@pytest.mark.parametrize("greek", ["delta", "gamma", "vega", "rho"])
def test_greeks_fd(call, greek):
    params = dict(St=100.0, K=105.0, T=1.0, r=0.03, sigma=0.25, call=call)

    analytical = hapi.get_greek_bs_european(**params, greek=greek)
    fd = hapi.get_greek_bs_european(
        **params,
        greek=greek,
        greek_engine="fd",
        engine="analytical",
    )

    assert fd == pytest.approx(analytical, abs=1e-5)


def test_greeks_mc_delta():
    params = dict(St=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, call=True)

    analytical = hapi.get_greek_bs_european(**params, greek="delta")
    mc = hapi.get_greek_bs_european(
        **params,
        greek="delta",
        greek_engine="fd",
        engine="mc",
        n_paths=50_000,
        seed=123,
    )

    assert mc == pytest.approx(analytical, abs=0.01)


def test_greeks_mc_needs_seed():
    with pytest.raises(ValueError, match="seed"):
        hapi.get_greek_bs_european(
            St=100.0,
            K=100.0,
            T=1.0,
            r=0.05,
            sigma=0.20,
            call=True,
            greek="delta",
            greek_engine="fd",
            engine="mc",
            n_paths=10_000,
        )


def test_greeks_h_convergence():
    params = dict(St=100.0, K=105.0, T=1.0, r=0.03, sigma=0.25, call=True)
    analytical = hapi.get_greek_bs_european(**params, greek="delta")

    central_coarse = hapi.get_greek_bs_european(
        **params,
        greek="delta",
        greek_engine="fd",
        engine="analytical",
        fd_scheme="central",
        h=1.0,
    )
    central_fine = hapi.get_greek_bs_european(
        **params,
        greek="delta",
        greek_engine="fd",
        engine="analytical",
        fd_scheme="central",
        h=0.1,
    )
    forward_coarse = hapi.get_greek_bs_european(
        **params,
        greek="delta",
        greek_engine="fd",
        engine="analytical",
        fd_scheme="forward",
        h=1.0,
    )
    forward_fine = hapi.get_greek_bs_european(
        **params,
        greek="delta",
        greek_engine="fd",
        engine="analytical",
        fd_scheme="forward",
        h=0.1,
    )

    central_coarse_error = abs(central_coarse - analytical)
    central_fine_error = abs(central_fine - analytical)
    forward_coarse_error = abs(forward_coarse - analytical)
    forward_fine_error = abs(forward_fine - analytical)

    assert central_fine_error < central_coarse_error / 50
    assert forward_fine_error < forward_coarse_error / 5


@pytest.mark.parametrize("greek_engine", ["analytical", "fd"])
@pytest.mark.parametrize("greek", ["delta", "gamma", "vega", "rho"])
def test_greeks_parity(greek_engine, greek):
    params = dict(St=100.0, K=105.0, T=0.75, r=0.04, sigma=0.22)

    call = hapi.get_greek_bs_european(
        **params,
        call=True,
        greek=greek,
        greek_engine=greek_engine,
    )
    put = hapi.get_greek_bs_european(
        **params,
        call=False,
        greek=greek,
        greek_engine=greek_engine,
    )

    if greek == "delta":
        expected = 1.0
    elif greek in {"gamma", "vega"}:
        expected = 0.0
    else:
        expected = params["K"] * params["T"] * math.exp(-params["r"] * params["T"])

    assert call - put == pytest.approx(expected, abs=1e-6)


@pytest.mark.parametrize("call, lower, upper", [(True, 0.0, 1.0), (False, -1.0, 0.0)])
def test_greeks_bounds(call, lower, upper):
    params = dict(St=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, call=call)

    delta = hapi.get_greek_bs_european(**params, greek="delta")
    gamma = hapi.get_greek_bs_european(**params, greek="gamma")
    vega = hapi.get_greek_bs_european(**params, greek="vega")

    assert lower <= delta <= upper
    assert gamma >= 0.0
    assert vega >= 0.0


def test_greeks_rho_consistency():
    params = dict(St=100.0, K=95.0, T=1.5, r=0.04, sigma=0.18, call=True)

    analytical = hapi.get_greek_bs_european(**params, greek="rho")
    fd = hapi.get_greek_bs_european(
        **params,
        greek="rho",
        greek_engine="fd",
        engine="analytical",
    )

    assert fd == pytest.approx(analytical, abs=1e-5)


@pytest.mark.parametrize(
    "kwargs, message",
    [
        (dict(greek="theta"), "greek"),
        (dict(engine="tree"), "engine"),
        (dict(greek_engine="pathwise"), "greek_engine"),
        (dict(greek_engine="fd", fd_scheme="bad"), "fd_scheme"),
        (dict(greek_engine="fd", h=0.0), "h"),
        (dict(greek_engine="fd", engine="mc"), "n_paths"),
        (dict(greek_engine="fd", engine="mc", n_paths=0), "n_paths"),
        (dict(greek_engine="fd", engine="mc", n_paths=10_000), "seed"),
        (dict(St=0.0), "Spot"),
        (dict(K=0.0), "Strike"),
        (dict(T=0.0), "Time"),
        (dict(sigma=0.0), "Volatility"),
    ],
)
def test_greeks_validation(kwargs, message):
    params = dict(
        St=100.0,
        K=100.0,
        T=1.0,
        r=0.05,
        sigma=0.20,
        call=True,
        greek="delta",
    )
    params.update(kwargs)

    with pytest.raises(ValueError, match=message):
        hapi.get_greek_bs_european(**params)
