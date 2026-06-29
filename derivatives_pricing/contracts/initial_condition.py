# derivatives_pricing/contracts/initial_condition.py

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class InitialCondition:
    """Adapter for a heat-equation initial condition.

    Args:
        func: Callable that maps the spatial grid to initial values.
    """

    func: Callable[[NDArray[np.float64]], NDArray[np.float64]]

    def __post_init__(self) -> None:
        if not callable(self.func):
            raise ValueError("initial_condition must be callable.")

    def values(self, x_grid: NDArray[np.float64]) -> NDArray[np.float64]:
        """Evaluate the initial condition on a spatial grid.

        Args:
            x_grid: Spatial grid where the initial condition is evaluated.

        Returns:
            Initial values with the same shape as ``x_grid``.

        Raises:
            ValueError: If the callable returns an incompatible shape.
        """
        values = np.asarray(self.func(x_grid), dtype=float)
        if values.shape == ():
            return np.full_like(x_grid, float(values), dtype=float)
        if values.shape != x_grid.shape:
            raise ValueError(
                "initial_condition must return values with the same shape "
                "as x_grid."
            )
        return values
