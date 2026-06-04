# hesperides/utils/normal.py

import math


def normal_cdf(x: float) -> float:
    """Compute the standard normal cumulative distribution function.

    Args:
        x: Evaluation point.

    Returns:
        Standard normal probability :math:`N(x)`.
    """
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def normal_pdf(x: float) -> float:
    """Compute the standard normal probability density function.

    Args:
        x: Evaluation point.

    Returns:
        Standard normal density :math:`\\varphi(x)`.
    """
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)
