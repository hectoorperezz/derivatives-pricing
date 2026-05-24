import pytest

import hesperides.api as hapi


@pytest.mark.parametrize("call", [True, False])
def test_european_mc_seed(call):
    params = dict(St=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, call=call)

    first = hapi.get_price_bs_european(
        **params, engine="mc", n_paths=20_000, seed=123
    )
    second = hapi.get_price_bs_european(
        **params, engine="mc", n_paths=20_000, seed=123
    )

    assert second == first


@pytest.mark.parametrize("call", [True, False])
def test_european_mc_price(call):
    params = dict(St=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, call=call)

    analytical = hapi.get_price_bs_european(**params)
    mc = hapi.get_price_bs_european(
        **params, engine="mc", n_paths=50_000, seed=123
    )

    assert mc == pytest.approx(analytical, abs=0.10)


@pytest.mark.parametrize("call", [True, False])
def test_asian_mc_seed(call):
    params = dict(St=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, call=call)

    first = hapi.get_price_bs_geometric_asian(
        **params, engine="mc", n_paths=20_000, n_steps=64, seed=123
    )
    second = hapi.get_price_bs_geometric_asian(
        **params, engine="mc", n_paths=20_000, n_steps=64, seed=123
    )

    assert second == first


@pytest.mark.parametrize("call", [True, False])
def test_asian_mc_price(call):
    params = dict(St=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, call=call)

    analytical = hapi.get_price_bs_geometric_asian(**params)
    mc = hapi.get_price_bs_geometric_asian(
        **params, engine="mc", n_paths=50_000, n_steps=64, seed=123
    )

    assert mc == pytest.approx(analytical, abs=0.15)


def test_european_mc_paths():
    params = dict(St=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, call=True)

    analytical = hapi.get_price_bs_european(**params)
    low_paths = hapi.get_price_bs_european(
        **params, engine="mc", n_paths=2_000, seed=123
    )
    high_paths = hapi.get_price_bs_european(
        **params, engine="mc", n_paths=100_000, seed=123
    )

    assert abs(high_paths - analytical) < abs(low_paths - analytical)


def test_asian_mc_paths():
    params = dict(St=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, call=False)

    analytical = hapi.get_price_bs_geometric_asian(**params)
    low_paths = hapi.get_price_bs_geometric_asian(
        **params, engine="mc", n_paths=2_000, n_steps=64, seed=123
    )
    high_paths = hapi.get_price_bs_geometric_asian(
        **params, engine="mc", n_paths=100_000, n_steps=64, seed=123
    )

    assert abs(high_paths - analytical) < abs(low_paths - analytical)


def test_asian_mc_steps():
    params = dict(St=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, call=True)

    analytical = hapi.get_price_bs_geometric_asian(**params)
    coarse_grid = hapi.get_price_bs_geometric_asian(
        **params, engine="mc", n_paths=50_000, n_steps=4, seed=321
    )
    fine_grid = hapi.get_price_bs_geometric_asian(
        **params, engine="mc", n_paths=50_000, n_steps=252, seed=321
    )

    assert abs(fine_grid - analytical) < abs(coarse_grid - analytical)
