# Assignment 3: Black–Scholes model, European and geometric Asian options

## Goal

Implement the **Black–Scholes** model and price two products under it:

1. **European options** (*call* and *put*) with standard terminal *payoff*.
2. **Geometric Asian options** (*call* and *put*) with *payoff* based on the continuous geometric average:

   $$
   G_T \coloneqq \exp\!\left(\frac{1}{T}\int_0^T \log S_u\,du\right).
   $$

Each product must have **two pricing engines**: **analytical** (closed form) and **Monte Carlo**. The solution must follow the modular architecture in the [README](../README.md) and expose entry points only through the `hesperides/api.py` *facade*.

For the Asian option via Monte Carlo, use the discrete approximation from module 5. European options do not need this time discretization.

Review the theory from modules 3, 4, and 5.

---

## API contract

Tests (public and private) will **only** import:

```python
import hesperides.api as hapi
```

Implement these *facade* functions in `hesperides/api.py` with the **exact** signatures below. `call` is boolean (`True` for *call*, `False` for *put*); `engine` is a literal that selects analytical vs Monte Carlo.

### European option under Black–Scholes

```python
def get_price_bs_european(
    St: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    call: bool,
    engine: str = "analytical",
    n_paths: int | None = None,
    seed: int | None = None,
) -> float:
    """
    Price a European option (call or put) under Black–Scholes.

    Parameters
    ----------
    St : float
        Spot price of the underlying at valuation date.
    K : float
        Strike.
    T : float
        Time to maturity in years.
    r : float
        Continuously compounded risk-free rate.
    sigma : float
        Black–Scholes volatility (annualized).
    call : bool
        True for call, False for put.
    engine : {"analytical", "mc"}, optional
        Pricing engine. Default "analytical".
    n_paths : int or None, optional
        Number of Monte Carlo paths. Required if engine="mc";
        ignored if engine="analytical".
    seed : int or None, optional
        Seed for reproducible Monte Carlo.

    Returns
    -------
    float
        Option price at valuation date.
    """
    ...
```

### Geometric Asian option under Black–Scholes

```python
def get_price_bs_geometric_asian(
    St: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    call: bool,
    engine: str = "analytical",
    n_paths: int | None = None,
    n_steps: int | None = None,
    seed: int | None = None,
) -> float:
    """
    Price a geometric Asian option (call or put) under Black–Scholes.

    Same parameters and meaning as ``get_price_bs_european``, with the addition of `n_steps`.

    Parameters
    ----------
    St, K, T, r, sigma, call, engine, n_paths, seed
        As in ``get_price_bs_european``.
    n_steps : int or None, optional
        Number of time steps in the Monte Carlo grid. Required if engine="mc".

    Returns
    -------
    float
        Option price at valuation date.
    """
    ...
```

`engine` must accept exactly `"analytical"` and `"mc"`; any other value raises `ValueError`. If `engine="mc"`, `n_paths` is required for both products and `n_steps` is required for the geometric Asian; passing `None` in either case raises `ValueError`.

---

## Requirements

### Architecture

- Follow the modular architecture and **single public interface** rule in the [main README](../README.md).
- Keep separation of **contract/instrument**, **market**, **model**, **engine**, and **pricer**:
  - **Model:** a `BlackScholesModel` class (or similar) parameterizing the dynamics and exposing what engines need.
  - **Simulation:** path simulation with `numpy.random.Generator`.
  - **Engines:** separate analytical and Monte Carlo engine classes. Each product composes with each engine; do not tie an engine to one *payoff*.
  - **Products:** the European *call* and *put* reuse the European option product from Assignment 1. The geometric Asian is a new product.
  - **Discount curve:** prefer something like `FlatDiscountCurve` with **continuous** convention (\(P(0,T) = e^{-rT}\)). Do not *hardcode* `np.exp(-r*T)` inside engines.

### Vectorization

- **Do not loop over paths:** Monte Carlo simulation and *payoff* must use NumPy (*broadcasting*, `cumsum`, `cumprod`, etc.).

### Reproducibility

- Monte Carlo must be reproducible via `seed`. Use `np.random.default_rng(seed)` and **do not** rely on NumPy's legacy global random state (`np.random.seed`, `np.random.normal`, `np.random.rand`, etc.).
- The same `seed` must yield the same pri77.

-
## Tests with `pytest`

Unlike earlier assignments, **no public tests** are provided. Validating your implementation is **part of the spec**: you design and write the test *suite* following this section. That mirrors professional practice where an external *oracle* is not always available.

Tests are a **deliverable** on par with library code.

- Tests in `tests/` per `pytest` conventions ([discovery and layout](https://docs.pytest.org/en/stable/goodpractices.html#choosing-a-test-layout-import-conventions-and-naming-conventions)); `pytest` as a *dev* dependency in `pyproject.toml`.
- Compare floats with `pytest.approx` (`rel`/`abs` as needed); arrays with `numpy.testing.assert_allclose`. Parametrize with `@pytest.mark.parametrize`; shared setup with `@pytest.fixture` (and `conftest.py` if useful). Contract errors with `pytest.raises` (optionally `match`). Declare markers (`slow`, `regression`, etc.) in `pyproject.toml` for `pytest -m`.
- Monte Carlo vs analytical: fixed `seed` and sensible tolerance (e.g. a few standard errors of the estimator; avoid tolerances so loose the test is meaningless).

### Minimum coverage

No fixed test count; you must at least cover:

- Analytical vs MC for European and geometric Asian, *call* and *put*, with sensible tolerance (as above).
- Convergence in `n_paths`: error decreases statistically/asymptotically as paths increase.
- Convergence in `n_steps` (where relevant): discretization bias decreases as the time grid refines.
- *Call*–*put* parity for both products (the geometric Asian parity uses the risk-neutral forward of the geometric average, not the spot).

---

## Submission checklist

Before submitting, check the general instructions in the [main README](../README.md). Submissions that cannot be installed and run will not be graded. Tests from earlier assignments may still be evaluated.

---

## References

- Privault, N. (2022). *Introduction to stochastic finance with market examples*. Chapman & Hall/CRC. Continuous geometric average Asian: **Exercise 13.5**.
- `pytest`: <https://docs.pytest.org/en/stable/>.
- NumPy random (`Generator`): <https://numpy.org/doc/stable/reference/random/generator.html>.
- [README](../README.md).
