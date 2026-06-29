# derivatives_pricing/market/data.py

from dataclasses import dataclass
from derivatives_pricing.market.base import DiscountCurve


@dataclass(frozen=True)
class MarketData:
    """Market observables: spot of the underlying and discount curve."""

    spot: float
    curve: DiscountCurve
