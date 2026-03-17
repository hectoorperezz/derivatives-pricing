# hesperides/api.py

from hesperides.contracts.european import EuropeanOption
from hesperides.market.curves import FlatDiscountCurve
from hesperides.models.binomial import BinomialModel
from hesperides.engines.binomial_engine import AnalyticBinomialEngine
from hesperides.pricers.european_pricer import EuropeanPricer


def get_price_binomial_european(
    St: float,
    K: float,
    T: int,
    R: float,
    u: float,
    d: float,
    call: bool,
) -> float:
    """Price a European call or put option using the binomial model."""
    contract = EuropeanOption(K=K, expiry=T, call=call)
    curve = FlatDiscountCurve(R=R)
    model = BinomialModel(u=u, d=d)
    engine = AnalyticBinomialEngine()
    pricer = EuropeanPricer(contract, model, curve, engine)

    return pricer.price(St)