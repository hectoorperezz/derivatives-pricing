# hesperides/models/heat_equation.py

from collections.abc import Callable
from dataclasses import dataclass


Boundary = float | Callable[[float], float]


@dataclass(frozen=True)
class HeatEquationModel:
    """One-dimensional heat-equation model with boundary conditions.

    Args:
        kappa: Diffusion coefficient in ``v_t = kappa * v_xx``.
        M: Right endpoint of the spatial domain ``[0, M]``.
        T: Final time.
        left_boundary: Left boundary value or slope, depending on
            ``boundary_type``.
        right_boundary: Right boundary value or slope, depending on
            ``boundary_type``.
        boundary_type: Boundary convention: ``"dirichlet"`` or ``"neumann"``.
    """

    kappa: float
    M: float
    T: float
    left_boundary: Boundary = 0.0
    right_boundary: Boundary = 0.0
    boundary_type: str = "dirichlet"

    def left_boundary_value(self, t: float) -> float:
        """Return the left boundary data at time ``t``.

        Args:
            t: Time at which the boundary is evaluated.

        Returns:
            Boundary value for Dirichlet, or slope for Neumann.
        """
        return self._boundary_value(self.left_boundary, t)

    def right_boundary_value(self, t: float) -> float:
        """Return the right boundary data at time ``t``.

        Args:
            t: Time at which the boundary is evaluated.

        Returns:
            Boundary value for Dirichlet, or slope for Neumann.
        """
        return self._boundary_value(self.right_boundary, t)

    @staticmethod
    def _boundary_value(boundary: Boundary, t: float) -> float:
        if callable(boundary):
            return float(boundary(t))
        return float(boundary)
