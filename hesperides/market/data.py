# hesperides/market/data.py

from dataclasses import dataclass
from hesperides.market.base import DiscountCurve


@dataclass(frozen=True)
class MarketData:
    """Market observables: spot of the underlying and discount curve."""

    spot: float
    curve: DiscountCurve
