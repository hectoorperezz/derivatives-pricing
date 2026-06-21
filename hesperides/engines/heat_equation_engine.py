# hesperides/engines/heat_equation_engine.py

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import solve_banded

from hesperides.contracts.initial_condition import InitialCondition
from hesperides.models.heat_equation import HeatEquationModel


@dataclass(frozen=True)
class HeatEquationEngine:
    """Finite-difference solver for the one-dimensional heat equation.

    Args:
        n_x: Number of spatial intervals.
        n_t: Number of time steps.
        scheme: Time-stepping scheme: ``"explicit"`` or ``"implicit"``.
    """

    n_x: int
    n_t: int
    scheme: str = "explicit"

    def solve(
        self,
        condition: InitialCondition,
        model: HeatEquationModel,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Solve the heat equation up to the model final time.

        Args:
            condition: Initial condition adapter.
            model: Heat-equation model with coefficients and boundaries.

        Returns:
            Spatial grid and final-time solution.
        """
        self._validate(model)
        x_grid, dx, dt, r = self._mesh(model)
        u = condition.values(x_grid)
        self._apply_boundaries(u, model, t=0.0, dx=dx)

        if self.scheme == "explicit":
            return self._solve_explicit(u, x_grid, dx, dt, r, model)
        return self._solve_implicit(u, x_grid, dx, dt, r, model)

    def _validate(self, model: HeatEquationModel) -> None:
        if self.scheme not in {"explicit", "implicit"}:
            raise ValueError("scheme must be 'explicit' or 'implicit'.")
        if model.boundary_type not in {"dirichlet", "neumann"}:
            raise ValueError("boundary_type must be 'dirichlet' or 'neumann'.")
        if model.kappa <= 0:
            raise ValueError("kappa must be positive.")
        if model.M <= 0:
            raise ValueError("M must be positive.")
        if model.T <= 0:
            raise ValueError("T must be positive.")
        if self.n_x < 1:
            raise ValueError("n_x must be at least 1.")
        if self.n_t < 1:
            raise ValueError("n_t must be at least 1.")

    def _mesh(
        self, model: HeatEquationModel
    ) -> tuple[NDArray[np.float64], float, float, float]:
        dx = model.M / self.n_x
        dt = model.T / self.n_t
        r = model.kappa * dt / dx**2
        x_grid = np.linspace(0.0, model.M, self.n_x + 1)
        return x_grid, dx, dt, r

    def _solve_explicit(
        self,
        u: NDArray[np.float64],
        x_grid: NDArray[np.float64],
        dx: float,
        dt: float,
        r: float,
        model: HeatEquationModel,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        for step in range(self.n_t):
            t_next = (step + 1) * dt
            u_new = u.copy()
            u_new[1:-1] = (
                r * u[:-2] + (1.0 - 2.0 * r) * u[1:-1] + r * u[2:]
            )
            self._apply_boundaries(u_new, model, t=t_next, dx=dx)
            u = u_new
        return x_grid, u

    def _solve_implicit(
        self,
        u: NDArray[np.float64],
        x_grid: NDArray[np.float64],
        dx: float,
        dt: float,
        r: float,
        model: HeatEquationModel,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        n_inner = self.n_x - 1
        if n_inner == 0:
            for step in range(self.n_t):
                t_next = (step + 1) * dt
                self._apply_boundaries(u, model, t=t_next, dx=dx)
            return x_grid, u

        ab = self._implicit_banded_matrix(
            r,
            n_inner,
            model.boundary_type,
        )

        for step in range(self.n_t):
            t_next = (step + 1) * dt
            rhs = u[1:-1].copy()
            self._adjust_implicit_rhs(rhs, model, t=t_next, dx=dx, r=r)
            u_new = u.copy()
            u_new[1:-1] = solve_banded((1, 1), ab, rhs)
            self._apply_boundaries(u_new, model, t=t_next, dx=dx)
            u = u_new
        return x_grid, u

    @staticmethod
    def _implicit_banded_matrix(
        r: float,
        n_inner: int,
        boundary_type: str,
    ) -> NDArray[np.float64]:
        lower = np.full(n_inner - 1, -r)
        main = np.full(n_inner, 1.0 + 2.0 * r)
        upper = np.full(n_inner - 1, -r)

        if boundary_type == "neumann":
            if n_inner == 1:
                main[0] = 1.0
            else:
                main[0] = 1.0 + r
                main[-1] = 1.0 + r

        ab = np.zeros((3, n_inner))
        ab[0, 1:] = upper
        ab[1, :] = main
        ab[2, :-1] = lower
        return ab

    @staticmethod
    def _adjust_implicit_rhs(
        rhs: NDArray[np.float64],
        model: HeatEquationModel,
        t: float,
        dx: float,
        r: float,
    ) -> None:
        left = model.left_boundary_value(t)
        right = model.right_boundary_value(t)

        if model.boundary_type == "dirichlet":
            rhs[0] += r * left
            rhs[-1] += r * right
            return

        rhs[0] -= r * dx * left
        rhs[-1] += r * dx * right

    @staticmethod
    def _apply_boundaries(
        u: NDArray[np.float64],
        model: HeatEquationModel,
        t: float,
        dx: float,
    ) -> None:
        left = model.left_boundary_value(t)
        right = model.right_boundary_value(t)

        if model.boundary_type == "dirichlet":
            u[0] = left
            u[-1] = right
            return

        u[0] = u[1] - dx * left
        u[-1] = u[-2] + dx * right
