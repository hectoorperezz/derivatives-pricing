# hesperides/greeks/bumps.py

from hesperides.market.curves import FlatDiscountCurve
from hesperides.market.data import MarketData
from hesperides.models.black_scholes import BlackScholesModel


def bump_spot(market: MarketData, h: float) -> MarketData:
    """Return market data with bumped spot.

    Args:
        market: Original market data.
        h: Additive spot bump.

    Returns:
        New market data with ``spot + h`` and the original curve.
    """
    return MarketData(spot=market.spot + h, curve=market.curve)


def bump_sigma(model: BlackScholesModel, h: float) -> BlackScholesModel:
    """Return a Black-Scholes model with bumped volatility.

    Args:
        model: Original Black-Scholes model.
        h: Additive volatility bump.

    Returns:
        New model with ``sigma + h``.
    """
    return BlackScholesModel(sigma=model.sigma + h, q=model.q)


def bump_rate(market: MarketData, h: float) -> MarketData:
    """Return market data with a bumped flat discount curve.

    Args:
        market: Original market data.
        h: Additive rate bump.

    Returns:
        New market data with the same spot and a curve with ``R + h``.

    Raises:
        ValueError: If the discount curve cannot be bumped.
    """
    if not isinstance(market.curve, FlatDiscountCurve):
        raise ValueError("Rate bumps require a FlatDiscountCurve.")
    curve = FlatDiscountCurve(
        R=market.curve.R + h,
        compounding=market.curve.compounding,
    )
    return MarketData(spot=market.spot, curve=curve)
