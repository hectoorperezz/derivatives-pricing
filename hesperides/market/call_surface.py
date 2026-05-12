# hesperides/market/call_surface.py

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class CallSurface:
    """Discrete European call-price surface C_{i,j} on a strikes x maturities grid.

    Rows are strikes, columns are maturities. `strikes` is optional: operations
    that require it (vertical and butterfly spreads) raise if it is None.
    """

    prices: NDArray[np.float64]
    strikes: NDArray[np.float64] | None = None

    def __post_init__(self) -> None:
        if self.strikes is None:
            return
        if self.strikes.shape[0] != self.prices.shape[0]:
            raise ValueError(
                f"Shape mismatch: prices has {self.prices.shape[0]} rows "
                f"but strikes has {self.strikes.shape[0]} entries."
            )
        if not np.all(np.diff(self.strikes) > 0):
            raise ValueError("Strikes must be strictly increasing.")

    def vertical_spreads(self) -> NDArray[np.float64]:
        r"""Normalized vertical call spreads.

        .. math::

            \bar{Q}_{i,j} \;=\; \frac{C_{i-1,j} - C_{i,j}}{K_i - K_{i-1}},
            \qquad i > 0.

        Returns array of shape :math:`(n_K - 1,\; n_T)`.
        """
        if self.strikes is None:
            raise ValueError("vertical_spreads requires strikes.")
        return -np.diff(self.prices, axis=0) / np.diff(self.strikes)[:, None]

    def butterfly_values(self) -> NDArray[np.float64]:
        r"""Interior butterfly spread values.

        .. math::

            \mathrm{BS}_{i,j} \;=\; C_{i-1,j}
            \,-\, \frac{K_{i+1} - K_{i-1}}{K_{i+1} - K_i}\, C_{i,j}
            \,+\, \frac{K_{i} - K_{i-1}}{K_{i+1} - K_i}\, C_{i+1,j}

        for :math:`i = 1, \ldots, n_K - 2`.
        Returns array of shape :math:`(n_K - 2,\; n_T)`.
        """
        if self.strikes is None:
            raise ValueError("butterfly_values requires strikes.")
        dK = np.diff(self.strikes)
        dK_left = dK[:-1]
        dK_right = dK[1:]
        dK_span = dK_left + dK_right
        return (
            self.prices[:-2]
            - (dK_span / dK_right)[:, None] * self.prices[1:-1]
            + (dK_left / dK_right)[:, None] * self.prices[2:]
        )

    def calendar_spreads(self) -> NDArray[np.float64]:
        r"""Calendar spreads across consecutive expiries.

        .. math::

            \mathrm{CS}_{i,j} \;=\; C_{i,j+1} - C_{i,j}.

        Returns array of shape :math:`(n_K,\; n_T - 1)`.
        """
        return np.diff(self.prices, axis=1)
