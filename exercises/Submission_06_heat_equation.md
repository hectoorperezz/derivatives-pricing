# Assignment 6: The heat equation by finite differences

## Goal

Build a small **finite-difference solver** for the one-dimensional heat equation and use it, through a change of variables, to **price a European option**. Two parts:

1. **The heat equation.** Solve

   $$
   v_t = \kappa\,v_{xx}, \qquad x \in (0, M),\; t \in (0, T],
   $$

   with initial condition $v(0, x) = f(x)$ and Dirichlet boundaries, using the **explicit** (FTCS) and **implicit** (BTCS) schemes. Study the stability of the explicit scheme (the **stability condition** $r \le \tfrac12$, read in the notes as a convex-combination bound) and validate against the known analytical solution.

2. **Black–Scholes through the heat equation (required).** The Black–Scholes PDE becomes the heat equation under the change of variables of *Fundamentos de Valoración*, Module 4. Use your heat solver to price a European call/put and **check that it matches the closed-form Black–Scholes price** of Assignment 3. This is the central deliverable: pricing a real option by solving a physics equation, and seeing the two answers coincide.

The solution must follow the modular architecture in the [README](../README.md) and expose entry points only through the `hesperides/api.py` *facade*. The heat equation is a *physical* problem with no payoff and no discounting, so reusing the pricing machinery (model / engine / market / product) for it is itself an architecture exercise: the model supplies the PDE coefficients and domain, the engine runs the finite-difference scheme, and a thin adapter carries the initial condition $f(x)$ in the place a payoff would normally sit.

---

## Theory (follow the numerical-methods lectures, Module 2)

The exact (continuous) solution is denoted $v(t, x)$; the **discrete approximation** at node $(t_n, x_j)$ is $u_j^n \approx v(t_n, x_j)$ (notes' convention). On a uniform mesh $x_j = j\,\Delta x$ ($\Delta x = M/n_x$), $t_n = n\,\Delta t$ ($\Delta t = T/n_t$), define the dimensionless ratio

$$
r := \frac{\kappa\,\Delta t}{\Delta x^2}.
$$

### Explicit scheme (FTCS)

Forward difference in time, centered second difference in space:

$$
u_j^{n+1} = (1 - 2r)\,u_j^n + r\,u_{j-1}^n + r\,u_{j+1}^n.
$$

The new value is a **weighted average** of the three old neighbours, with weights $(1-2r,\, r,\, r)$ summing to $1$. When $0 \le r \le \tfrac12$ all three weights are non-negative, so the update is a **convex combination** of its neighbours and cannot amplify the solution. This is the explicit scheme's **stability condition** (numerical-methods notes, Module 2 — the convex-combination / weighted-average reading):

$$
0 \le r \le \tfrac12, \qquad\text{i.e.}\qquad \kappa\,\Delta t \le \tfrac12\,\Delta x^2.
$$

(This parabolic bound is sometimes loosely called a CFL condition, but CFL proper is the domain-of-dependence condition for *hyperbolic* problems; the notes keep the convex-combination name.) If $r > \tfrac12$ the weight $1 - 2r$ turns negative, the average is no longer convex, and the scheme is **unstable**: the **alternating mode** $\phi_j = (-1)^j$ is amplified by a factor $|1 - 4r| > 1$ each step, so high-frequency (saw-tooth) errors grow without bound. Refining $\Delta x$ then forces a quadratically smaller $\Delta t$.

### Implicit scheme (BTCS)

Backward difference in time gives, at each step, a tridiagonal linear system

$$
-r\,u_{j-1}^{n+1} + (1 + 2r)\,u_j^{n+1} - r\,u_{j+1}^{n+1} = u_j^{n},
$$

which is **unconditionally stable**: any $\Delta t > 0$ works, at the cost of solving a tridiagonal system per step. Both schemes have truncation error $O(\Delta t) + O(\Delta x^2)$.

### Black–Scholes through the heat equation (required)

With $\tau = T - t$, $x = e^{\sigma y + (\sigma^2/2 - r)t}$ and $G(t, y) = e^{rt}F(\tau, x)$ (Module 4), the Black–Scholes PDE for the price $F$ of a European payoff $\Phi$ becomes the heat equation

$$
G_t = \tfrac12\,G_{yy}, \qquad G(0, y) = \Phi(e^{\sigma y}).
$$

So $\kappa = \tfrac12$ and the initial condition is the payoff written in the $y$ variable, e.g. $(e^{\sigma y} - K)^+$ for a call. Integrating the heat equation forward in $t$ from $0$ (maturity) to $T$ (today) on a truncated $y$-domain and inverting the change of variables gives the price

$$
F(0, S_0) = e^{-rT}\,G(T, y_0), \qquad
y_0 = \frac{\ln S_0 - (\sigma^2/2 - r)\,T}{\sigma}.
$$

The boundaries of the truncated domain are **asymptotic Dirichlet boundary conditions**: at each boundary node you prescribe the option value implied by the deep in/out-of-the-money asymptotics (zero on the out-of-the-money side, linear intrinsic-value behaviour on the in-the-money side). This is the required closure for `get_price_bs_european_heat`. Do not replace it by a Neumann or gamma-zero closure for the required facade; those are different numerical boundary closures discussed in the notes, but not the contract here. With a sufficiently wide domain the truncation error is negligible.

---

## API contract

Tests (public and private) will **only** import:

```python
import hesperides.api as hapi
```

Implement these *facade* functions in `hesperides/api.py` with the **exact** signatures below.

### Heat-equation solver

```python
def solve_heat_equation(
    initial_condition,            # callable f(x): np.ndarray -> np.ndarray
    kappa: float,
    M: float,
    T: float,
    n_x: int,
    n_t: int,
    scheme: str = "explicit",     # {"explicit", "implicit"}
    left_boundary=0.0,            # float or callable of the time grid
    right_boundary=0.0,
    boundary_type: str = "dirichlet",
):
    """
    Solve v_t = kappa * v_xx on [0, M] x (0, T] by finite differences.

    Returns
    -------
    (x_grid, u_T) : tuple[np.ndarray, np.ndarray]
        The spatial grid (n_x + 1 nodes) and the numerical solution u(T, .),
        the engine's approximation to the exact v(T, .), on it.
    """
    ...
```

### European option priced through the heat equation

```python
def get_price_bs_european_heat(
    St: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    call: bool,
    n_x: int = 400,
    n_t: int = 400,
    scheme: str = "implicit",
) -> float:
    """
    Price a European call/put by reducing Black–Scholes to the heat
    equation and solving it with ``solve_heat_equation`` using asymptotic
    Dirichlet boundary conditions on the truncated heat domain. Must agree
    with ``get_price_bs_european`` (Assignment 3) up to the discretization
    error.
    """
    ...
```

`scheme` must accept exactly `"explicit"` and `"implicit"`; any other value raises `ValueError`. In `solve_heat_equation`, `boundary_type` must be `"dirichlet"` or `"neumann"`; `kappa`, `M`, `T` must be `> 0`; `n_x`, `n_t` must be `>= 1`. In `get_price_bs_european_heat`, non-positive `sigma`/`K`/`St`/`T` raise `ValueError`.

---

## Requirements

### Architecture

- Follow the modular architecture and **single public interface** rule in the [main README](../README.md).
- **Model**: a heat / 1D-PDE model that exposes the PDE coefficients ($\kappa$, or more generally drift / diffusion / rate) and the spatial domain $[0, M]$, plus its boundary conditions.
- **Engine**: a *generic* 1D finite-difference engine implementing the **explicit** and **implicit** schemes. The spatial second-difference operator is the same for both; only the time update differs. The implicit step must solve the tridiagonal system **vectorized** (no Python loop over interior nodes — use a banded/tridiagonal solve).
- **Initial-condition adapter**: the heat equation has no payoff. Provide a single, reusable product-like adapter that carries the initial condition $f(x)$ through the engine in the place a payoff would sit. Define it **once** and reuse it for both `solve_heat_equation` and `get_price_bs_european_heat` (and your tests) — do not redefine the same toy class in several files.
- Keep the change of variables (Black–Scholes $\to$ heat) out of the engine: it belongs to the facade / a small helper, so the engine stays a pure heat-equation solver.

### Numerical issues

- The **explicit scheme is stable only for $r = \kappa\,\Delta t/\Delta x^2 \le \tfrac12$**; demonstrate the saw-tooth blow-up when $r > \tfrac12$.
- Report the **convergence order**: refining the mesh, the error against the analytical solution should decrease like $O(\Delta x^2) + O(\Delta t)$.
- Handle the Dirichlet boundary nodes explicitly; do not let them drift.

### Reproducibility

- The solver is deterministic; no RNG is involved. The same inputs must give the same grid and solution.

---

## Optional extension*: barrier options

> Marked with an asterisk: **not required**, and harder. Offered for students who want to price something beyond vanilla calls and puts.

Vanilla call/put boundaries are only a *numerical* truncation with no contractual meaning. **Barrier options** are where boundary conditions become the contract itself (numerical-methods lectures, Module 3). In an **up-and-out** call, the option is extinguished if the underlying touches an upper barrier $H$ before maturity; numerically this is a **homogeneous Dirichlet condition imposed at the barrier**, $v = 0$ there — not an asymptotic approximation but a clause of the contract. Implement a knock-out barrier option on top of your PDE engine by placing the barrier on the grid and pinning the boundary value, and validate the limiting cases (a barrier far from the spot recovers the vanilla price; a barrier at the spot kills the option). Expose it through a separate optional entry point.

---

## Tests with `pytest`

As in Assignments 3–5, **no public tests are provided**. The test suite is a deliverable; include your tests in the `.whl`. In particular, the Black–Scholes $\leftrightarrow$ heat-equation agreement **must be checked by a test you write**.

- Tests in `tests/` per `pytest` conventions; `pytest` as a *dev* dependency in `pyproject.toml`.
- Compare floats with `pytest.approx` and arrays with `numpy.testing.assert_allclose`; parametrize with `@pytest.mark.parametrize`; contract errors with `pytest.raises(match=...)`.

### Minimum coverage

No fixed test count; you must at least cover:

- **Analytical validation**: for a sine initial condition $f(x) = \sin(\pi x / M)$ with homogeneous Dirichlet boundaries, the exact solution is $v(T, x) = e^{-\kappa(\pi/M)^2 T}\sin(\pi x/M)$; both schemes must match it (explicit only with $r \le \tfrac12$).
- **Stability threshold**: the explicit scheme stays bounded for $r \le \tfrac12$ and **diverges** for $r$ clearly above $\tfrac12$.
- **Convergence order** in $\Delta x$ (and $\Delta t$) against the analytical solution.
- **Implicit stability**: the implicit scheme stays accurate with a large $\Delta t$ that would break the explicit scheme.
- **Black–Scholes $\leftrightarrow$ heat (required)**: `get_price_bs_european_heat(...)` agrees with `get_price_bs_european(...)` for both a call and a put, across a few strikes/maturities, within a sensible tolerance.
- **Validation**: each `ValueError` branch in the API contract.

---

## Submission checklist

Before submitting, check the general instructions in the [main README](../README.md). Submissions that cannot be installed and run will not be graded. Tests from earlier assignments may still be evaluated.

---

## References

### Course modules

- **Métodos numéricos para EDPs** (numerical methods for PDEs), **Module 2: "Introducción a las diferencias finitas"** — the heat equation, the FTCS and BTCS schemes, the **stability condition** $r = \kappa\,\Delta t/\Delta x^2 \le \tfrac12$ in its convex-combination (weighted-average) reading, the alternating-mode blow-up for $r > \tfrac12$, truncation error, and consistency + stability $\Rightarrow$ convergence (Lax equivalence).
- **Métodos numéricos para EDPs** (numerical methods for PDEs), **Module 3** — terminal PDE problems, boundary conditions and the barrier example (up-and-out as a homogeneous Dirichlet condition at the barrier), for the optional extension.
- **Fundamentos de Valoración** (asset-pricing fundamentals), **Module 4** — Black–Scholes through the heat equation: the change of variables $\tau = T-t$, $x = e^{\sigma y + (\sigma^2/2 - r)t}$, $G = e^{rt}F$, the heat kernel and the closed-form European prices.

### Tooling

- `pytest`: <https://docs.pytest.org/en/stable/>.
- NumPy: <https://numpy.org/doc/stable/>.
- [Main README](../README.md).
