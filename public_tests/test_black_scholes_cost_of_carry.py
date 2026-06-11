import math

import pytest

import hesperides.api as hapi


DIVIDEND_PARAMS = dict(
    St=100.0,
    K=105.0,
    T=1.0,
    r=0.03,
    q=0.01,
    sigma=0.25,
)

FUTURE_PARAMS = dict(
    F0=100.0,
    K=98.0,
    T=0.75,
    r=0.04,
    sigma=0.20,
)


@pytest.mark.parametrize("call", [True, False])
def test_dividend_recovery(call):
    params = dict(St=100.0, K=105.0, T=1.0, r=0.03, sigma=0.25, call=call)

    plain = hapi.get_price_bs_european(**params)
    dividend = hapi.get_price_bs_european_dividend(**params, q=0.0)

    assert dividend == pytest.approx(plain, abs=1e-12)


@pytest.mark.parametrize(
    "call, expected",
    [
        (True, 8.612435613890776),
        (False, 11.504233261567334),
    ],
)
def test_dividend_reference(call, expected):
    # Reference values generated offline with QuantLib 1.42.1.
    # QuantLib is not a project dependency.
    value = hapi.get_price_bs_european_dividend(
        **DIVIDEND_PARAMS,
        call=call,
    )

    assert value == pytest.approx(expected, abs=1e-10)


def test_dividend_parity():
    params = dict(DIVIDEND_PARAMS)

    call = hapi.get_price_bs_european_dividend(**params, call=True)
    put = hapi.get_price_bs_european_dividend(**params, call=False)
    expected = params["St"] * math.exp(-params["q"] * params["T"]) - params[
        "K"
    ] * math.exp(-params["r"] * params["T"])

    assert call - put == pytest.approx(expected, abs=1e-10)


@pytest.mark.parametrize("call", [True, False])
def test_dividend_reduction(call):
    params = dict(DIVIDEND_PARAMS, call=call)
    adjusted_spot = params["St"] * math.exp(-params["q"] * params["T"])

    dividend = hapi.get_price_bs_european_dividend(**params)
    plain = hapi.get_price_bs_european(
        St=adjusted_spot,
        K=params["K"],
        T=params["T"],
        r=params["r"],
        sigma=params["sigma"],
        call=call,
    )

    assert dividend == pytest.approx(plain, abs=1e-10)


@pytest.mark.parametrize("call", [True, False])
def test_fx_symmetry(call):
    params = dict(St=1.10, K=1.05, T=1.0, r_d=0.03, r_f=0.01, sigma=0.18)

    fx = hapi.get_price_fx_option(**params, call=call)
    dividend = hapi.get_price_bs_european_dividend(
        St=params["St"],
        K=params["K"],
        T=params["T"],
        r=params["r_d"],
        sigma=params["sigma"],
        call=call,
        q=params["r_f"],
    )

    assert fx == pytest.approx(dividend, abs=1e-12)


def test_fx_zero_foreign_rate():
    params = dict(St=1.10, K=1.05, T=1.0, r_d=0.03, sigma=0.18, call=True)

    fx = hapi.get_price_fx_option(**params, r_f=0.0)
    plain = hapi.get_price_bs_european(
        St=params["St"],
        K=params["K"],
        T=params["T"],
        r=params["r_d"],
        sigma=params["sigma"],
        call=params["call"],
    )

    assert fx == pytest.approx(plain, abs=1e-12)


@pytest.mark.parametrize(
    "call, expected",
    [
        (True, 7.645702221700777),
        (False, 5.704811154603767),
    ],
)
def test_future_reference(call, expected):
    # Reference values generated offline with QuantLib 1.42.1 blackFormula.
    # QuantLib is not a project dependency.
    value = hapi.get_price_future_option(
        **FUTURE_PARAMS,
        call=call,
    )

    assert value == pytest.approx(expected, abs=1e-10)


@pytest.mark.parametrize("call", [True, False])
def test_future_symmetry(call):
    params = dict(FUTURE_PARAMS)

    future = hapi.get_price_future_option(**params, call=call)
    dividend = hapi.get_price_bs_european_dividend(
        St=params["F0"],
        K=params["K"],
        T=params["T"],
        r=params["r"],
        sigma=params["sigma"],
        call=call,
        q=params["r"],
    )

    assert future == pytest.approx(dividend, abs=1e-12)


def test_future_parity():
    params = dict(FUTURE_PARAMS)

    call = hapi.get_price_future_option(**params, call=True)
    put = hapi.get_price_future_option(**params, call=False)
    expected = math.exp(-params["r"] * params["T"]) * (params["F0"] - params["K"])

    assert call - put == pytest.approx(expected, abs=1e-10)


def test_future_zero_rate():
    params = dict(F0=100.0, K=98.0, T=0.75, r=0.0, sigma=0.20, call=True)

    future = hapi.get_price_future_option(**params)
    plain = hapi.get_price_bs_european(
        St=params["F0"],
        K=params["K"],
        T=params["T"],
        r=params["r"],
        sigma=params["sigma"],
        call=params["call"],
    )

    assert future == pytest.approx(plain, abs=1e-12)


@pytest.mark.parametrize(
    "pricing_function, params",
    [
        (
            hapi.get_price_bs_european_dividend,
            dict(DIVIDEND_PARAMS, call=True, q=0.02),
        ),
        (
            hapi.get_price_future_option,
            dict(FUTURE_PARAMS, call=True),
        ),
    ],
)
def test_cost_of_carry_mc(pricing_function, params):
    analytical = pricing_function(**params)
    mc = pricing_function(
        **params,
        engine="mc",
        n_paths=100_000,
        seed=123,
    )

    assert mc == pytest.approx(analytical, abs=0.15)


@pytest.mark.parametrize(
    "pricing_function, kwargs, message",
    [
        (
            hapi.get_price_bs_european_dividend,
            dict(engine="tree"),
            "engine",
        ),
        (
            hapi.get_price_bs_european_dividend,
            dict(engine="mc"),
            "n_paths",
        ),
        (
            hapi.get_price_bs_european_dividend,
            dict(engine="mc", n_paths=0),
            "n_paths",
        ),
        (
            hapi.get_price_bs_european_dividend,
            dict(St=0.0),
            "Spot",
        ),
        (
            hapi.get_price_future_option,
            dict(F0=0.0),
            "Future price",
        ),
        (
            hapi.get_price_bs_european_dividend,
            dict(K=0.0),
            "Strike",
        ),
        (
            hapi.get_price_bs_european_dividend,
            dict(T=-1.0),
            "Time",
        ),
        (
            hapi.get_price_bs_european_dividend,
            dict(sigma=0.0),
            "Volatility",
        ),
    ],
)
def test_cost_of_carry_validation(pricing_function, kwargs, message):
    params = dict(St=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, call=True, q=0.02)
    if pricing_function is hapi.get_price_future_option:
        params = dict(F0=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, call=True)
    params.update(kwargs)

    with pytest.raises(ValueError, match=message):
        pricing_function(**params)
