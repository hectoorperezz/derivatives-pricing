import pytest

import hesperides.api as hapi


def test_invalid_engine():
    with pytest.raises(ValueError, match="engine"):
        hapi.get_price_bs_european(
            St=100.0,
            K=100.0,
            T=1.0,
            r=0.05,
            sigma=0.20,
            call=True,
            engine="tree",
        )


def test_mc_needs_paths():
    with pytest.raises(ValueError, match="n_paths"):
        hapi.get_price_bs_european(
            St=100.0,
            K=100.0,
            T=1.0,
            r=0.05,
            sigma=0.20,
            call=True,
            engine="mc",
        )


def test_asian_mc_needs_steps():
    with pytest.raises(ValueError, match="n_steps"):
        hapi.get_price_bs_geometric_asian(
            St=100.0,
            K=100.0,
            T=1.0,
            r=0.05,
            sigma=0.20,
            call=True,
            engine="mc",
            n_paths=10_000,
        )
