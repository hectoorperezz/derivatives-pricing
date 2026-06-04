# Assignment 4: Greeks for European options under Black–Scholes

## Goal

Implement the four main **Greeks** of a European option under the Black–Scholes model. The facade exposes two orthogonal axes:

- a **pricing engine** (`engine`) — `"analytical"` (closed-form Black–Scholes price) or `"mc"` (Monte Carlo);
- a **Greek engine** (`greek_engine`) — `"analytical"` (closed-form derivative of the BS price; no pricing engine involved) or `"fd"` (finite-difference bump-and-reprice applied to whichever pricing engine is selected).

Together they cover the three meaningful regimes:

1. **`greek_engine="analytical"`** — closed-form Black–Scholes Greeks. The production method for vanilla European options under Black–Scholes, and the reference value used to validate any other estimator. The `engine` argument plays no role here (analytical Greeks do not involve a pricer).
2. **`greek_engine="fd"`, `engine="analytical"`** — finite-difference bump-and-reprice on the analytical pricer. With no Monte Carlo noise, only the truncation bias of the FD scheme is visible: this is an **isolated sanity test** of the bump-and-reprice machinery, not the production reason FD exists.
3. **`greek_engine="fd"`, `engine="mc"`** — finite-difference bump-and-reprice on the Monte Carlo pricer. This is the **production scenario** for which bump-and-reprice was originally devised: the price is itself a noisy estimate and no closed form is available, so analytical Greeks vanish. Validating it against the closed-form Greeks (regime 1) is the comparison the lecture notes (*Métodos numéricos*, Mod. 1) are built around.

The Greeks to implement are

- **Delta** $\Delta = \partial V/\partial S_t$,
- **Gamma** $\Gamma = \partial^2 V/\partial S_t^2$,
- **Vega**  $\mathcal{V} = \partial V/\partial \sigma$,
- **Rho**   $\rho = \partial V/\partial r$.

Reuse the European option product, the Black–Scholes model, and the Monte Carlo engine from Assignment 3. The solution must follow the modular architecture in the [README](../README.md) and expose entry points only through the `hesperides/api.py` *facade*.

Theoretical background:

- **Métodos numéricos y simulación estocástica** (course on numerical methods for derivatives pricing), **Module 1: "Cálculo de griegas por Monte Carlo"** — primary reference. Definitions of the Greeks, finite-difference estimators (forward, central, Richardson, MSE/RMSE optimal-bump analysis), pathwise method, likelihood-ratio method, and practical bump policies. *Bump-and-reprice* is introduced there as the natural method when no closed-form Greek is available; that is the scenario the FD-over-MC composition targets.
- **Fundamentos de Valoración** (course on asset-pricing fundamentals), **Module 4** — closed-form Black–Scholes European prices and analytical Greeks (delta, gamma, vega, rho) from the heat-equation solution.
- **Fundamentos de Valoración** (course on asset-pricing fundamentals), **Module 5** — Monte Carlo fundamentals and the exact-step Black–Scholes scheme reused from Assignment 3.

---

## API contract

Tests (public and private) will **only** import:

```python
import hesperides.api as hapi
```

Implement this *facade* function in `hesperides/api.py` with the **exact** signature below.

```python
def get_greek_bs_european(
    St: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    call: bool,
    greek: str,
    engine: str = "analytical",
    greek_engine: str = "analytical",
    fd_scheme: str = "central",
    h: float | None = None,
    n_paths: int | None = None,
    seed: int | None = None,
) -> float:
    """
    Compute a Greek of a European call/put under Black–Scholes.

    Two orthogonal axes drive the computation:

    * ``engine`` selects the underlying *pricing* engine: ``"analytical"``
      (closed-form Black–Scholes price) or ``"mc"`` (Monte Carlo).
    * ``greek_engine`` selects the *Greek* method: ``"analytical"``
      (closed-form derivative of the BS price; no pricing engine
      involved) or ``"fd"`` (finite-difference bump-and-reprice of the
      configured pricing engine).

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
    greek : {"delta", "gamma", "vega", "rho"}
        Which sensitivity to return.
    engine : {"analytical", "mc"}, optional
        Pricing engine. Used only when ``greek_engine="fd"``. With
        ``engine="analytical"`` the FD engine wraps the closed-form
        pricer (sanity test, no Monte Carlo noise). With ``engine="mc"``
        it wraps the Monte Carlo pricer (production scenario; requires
        both ``n_paths`` and a fixed ``seed`` so bumped repricings share
        the same random numbers). Default
        ``"analytical"``.
    greek_engine : {"analytical", "fd"}, optional
        Greek computation method. ``"analytical"`` returns the
        closed-form Black-Scholes Greek directly; after selector
        validation, ``fd_scheme``, ``h``, ``n_paths`` and ``seed`` are
        ignored. ``"fd"`` applies finite-difference bump-and-reprice on
        top of the chosen ``engine``. Default ``"analytical"``.
    fd_scheme : {"forward", "central"}, optional
        Finite-difference scheme for first-order Greeks. Only used when
        ``greek_engine="fd"``. Default ``"central"``. Gamma always uses
        the central second-difference regardless of this argument (a
        second derivative needs evaluations at +h, 0 and -h).
    h : float or None, optional
        Bump size, applied additively in the natural units of whichever
        parameter is being bumped (St for delta/gamma, sigma for vega,
        r for rho). If None, choose sensible per-parameter defaults;
        the default spot bump may be proportional to St. Only used when
        ``greek_engine="fd"``.
    n_paths : int or None, optional
        Number of Monte Carlo paths. Required when
        ``greek_engine="fd"`` and ``engine="mc"``; ignored otherwise.
    seed : int or None, optional
        Seed for the Monte Carlo engine. Required when
        ``greek_engine="fd"`` and ``engine="mc"`` so the bumped
        repricings use common random numbers. Ignored otherwise.

    Returns
    -------
    float
        The requested Greek.
    """
    ...
```

`greek` must accept exactly `"delta"`, `"gamma"`, `"vega"`, `"rho"`; any other value raises `ValueError`. `engine` must accept exactly `"analytical"` and `"mc"`; any other value raises `ValueError`. `greek_engine` must accept exactly `"analytical"` and `"fd"`; any other value raises `ValueError`. These three selector validations always run, even when `greek_engine="analytical"`. When `greek_engine="fd"`: `fd_scheme` must be `"forward"` or `"central"`; `h` must be `> 0` when supplied; and when additionally `engine="mc"`, both `n_paths` (`> 0`) and `seed` are required. Non-positive `T`/`St`/`K`/`sigma` also raise `ValueError`. Vega and Rho are returned per unit change in `sigma` and `r`, not per volatility point or basis point.

For `greek_engine="analytical"`, after validating the selectors above, `fd_scheme`, `h`, `n_paths` and `seed` are **ignored** (do not raise).

---

## Requirements

### Architecture

- Follow the modular architecture and **single public interface** rule in the [main README](../README.md).
- Implement a **Greeks engine layer** with at least:
  - a concrete **closed-form** engine for the Black–Scholes Greeks of a European option;
  - a **finite-difference** engine that **wraps compatible pricing engines** — both the analytic Black–Scholes pricer and the Monte Carlo pricer from Assignment 3. The two compositions are exposed through the facade as `(engine="analytical", greek_engine="fd")` and `(engine="mc", greek_engine="fd")` respectively; the same FD code path serves both.
- The FD engine must consume **freshly constructed** bumped model/curve objects — **do not mutate** the caller's inputs. Provide bump helpers in their own module that return new instances of the model and discount curve.
- The closed-form Black–Scholes Greeks must reuse the conventions established in Assignment 3 (continuous discount factor $P(0,T) = e^{-rT}$ from the discount curve and Black–Scholes variance $\sigma^2 T$ from the model).

### Rho consistency (explicit requirement)

> When bumping `r`, the **same** shift must be applied to **both** the model's drift and the discount curve. Bumping only the model rate yields a Rho that is wrong by an order of magnitude and will fail the analytical-vs-FD comparison.

### Numerical issues

- `forward` scheme has bias $O(h)$; `central` has bias $O(h^2)$ (see *Métodos numéricos*, Mod. 1, Sec. "Diferencia centrada" and Glasserman 2004, Sec. 7.1, Table 7.1).
- Choose and document sensible default bump sizes. They must be additive bumps in the natural units of each parameter and should follow the order-of-magnitude conventions discussed in *Métodos numéricos*, Mod. 1, Sec. "Reglas prácticas".
- For `greek == "gamma"`, `fd_scheme` is **ignored**: a second derivative needs evaluations at $+h$, $0$ and $-h$, so the central second-difference $(V(x+h) - 2V(x) + V(x-h))/h^2$ is always used (cf. *Métodos numéricos*, Mod. 1, Sec. "Derivadas segundas" — the $1/h^2$ amplification already makes gamma harder than first-order Greeks; mixing a forward asymmetry on top would only worsen it).


### Reproducibility and common random numbers

The composition `greek_engine="fd"` + `engine="mc"` is the production scenario the FD engine exists for. As soon as the FD engine wraps the Monte Carlo pricer the price is a random estimate, and how the randomness is coupled across bumped repricings becomes critical:

- **Common Random Numbers (CRN) are required for FD over MC.** Each bumped repricing must use the **same** seed (equivalently, the same underlying uniform/normal sample). With CRN the variance of the difference of prices is $O(h^2)$; with independent sampling it stays $O(1)$, and the FD estimator becomes useless (Glasserman 2004, Sec. 7.1, Table 7.1; *Métodos numéricos*, Mod. 1, Sec. "La varianza depende del acoplamiento"). Therefore, when `greek_engine="fd"` and `engine="mc"`, the facade must raise `ValueError` if `seed is None`.
- Assignment 3's reproducibility rules apply throughout: use `np.random.default_rng(seed)`, never the legacy global RNG.

With `greek_engine="fd"` and `engine="analytical"`, both engines are deterministic and `seed`/`n_paths` play no role.

---

## Optional extension*: Monte Carlo Greeks (pathwise + LRM)

> Marked with an asterisk: **not required** for the base deliverable; offered for students who want to go further. Grading targets only the required Greek engines (`"analytical"` and `"fd"`).

The production scenario the FD engine was designed for is **FD over a Monte Carlo pricer with CRN**, validated against the analytical Black–Scholes Greeks. Pathwise and LRM are the **unbiased** alternatives the lecture notes contrast against that baseline — they avoid the bump entirely by differentiating the path or the density rather than repricing.

If you choose to tackle this, add a separate optional entry point rather than changing the exact facade signature above. That optional entry point may accept the additional `greek_engine` values `"pathwise"` and `"lrm"` (still alongside `engine="mc"`, with `n_paths` required and `seed` recommended). The base grading contract remains the exact signature above with `greek_engine ∈ {"analytical", "fd"}` and `engine ∈ {"analytical", "mc"}`. References:

- **Pathwise** — *Métodos numéricos*, Mod. 1, Sec. 2 ("Métodos insesgados: *pathwise*") and Glasserman (2004), Sec. 7.2. Implement the estimators following the derivations in the notes. The pathwise formulas covered there are first-order estimators; reject `greek_engine="pathwise"` for `greek="gamma"`.

- **Likelihood-Ratio Method (LRM)** — *Métodos numéricos*, Mod. 1, Sec. 3 ("Métodos insesgados: *likelihood ratio method*") and Glasserman (2004), Sec. 7.3. Implement the estimators by differentiating the density, following the notes.

---

## Tests with `pytest`

As in Assignment 3, **no public tests are provided**. Designing and writing the test suite is part of the spec, and tests are a deliverable on par with library code.

You must include in the `.whl` the tests you used for your submission. We will evaluate your delivery with private tests, but your wheel must also contain your own tests: after installing the wheel in a clean environment, we must be able to access the packaged tests folder and run those tests with `pytest` if needed. The README validation flow is only an analogy for checking this from a clean installation; it does not prescribe the exact command we will run. Do not send tests separately as a `.zip`: include them correctly in the wheel, just as you would include any other module or package distributed with your project.

- Tests in `tests/` per `pytest` conventions ([discovery and layout](https://docs.pytest.org/en/stable/goodpractices.html#choosing-a-test-layout-import-conventions-and-naming-conventions)); `pytest` as a *dev* dependency in `pyproject.toml`.
- Compare floats with `pytest.approx` (`rel`/`abs` as needed). Parametrize with `@pytest.mark.parametrize`. Contract errors with `pytest.raises(match=...)`. Declare markers (`slow`, `regression`, etc.) in `pyproject.toml` for `pytest -m`.

### Minimum coverage

No fixed test count; you must at least cover:

- Closed-form regression against a textbook reference for all four Greeks, *call* and *put* (`greek_engine="analytical"`).
- FD-engine sanity test: with `greek_engine="fd"` and `engine="analytical"` (no Monte Carlo noise, only truncation bias visible), the result must agree with the closed-form Greek for each Greek under `fd_scheme="central"` with the default bump sizes.
- **FD over Monte Carlo with CRN**: with `greek_engine="fd"`, `engine="mc"`, and a fixed `seed`, the FD result must agree with the closed-form Greek within the Monte Carlo error for at least one Greek (e.g., delta). Also test that omitting `seed` in this regime raises `ValueError`. This is the production scenario the FD engine was designed for, and the comparison that the lecture notes are built around.
- Convergence in $h$: refining the bump improves the FD-vs-analytical error at the expected order (central $\sim h^2$, forward $\sim h$) until floating-point noise dominates.
- *Call*–*put* parity per Greek for both Greek engines (delta differs by 1, gamma and vega coincide, rho difference equals $K\,T\,e^{-rT}$).
- Sign and bound checks: delta in $[0,1]$ (call) and $[-1,0]$ (put); gamma and vega non-negative.
- Rho-consistency regression: analytical rho and FD rho via the facade must agree (this catches the bug of bumping only the model rate without bumping the discount curve).
- Validation: each `ValueError` branch declared in the API contract section above.

The maturity boundary `T == 0` is not priced; it must raise `ValueError` under the API contract above.

---

## Submission checklist

Before submitting, check the general instructions in the [main README](../README.md). Submissions that cannot be installed and run will not be graded. Tests from earlier assignments may still be evaluated.

---

## References

### Course modules

- **Métodos numéricos y simulación estocástica** (course on numerical methods for derivatives pricing), **Module 1: "Cálculo de griegas por Monte Carlo"** — primary reference for the assignment. Covers definitions of the Greeks, finite differences (forward, central, Richardson extrapolation, optimal-bump MSE/RMSE analysis), the pathwise method, the likelihood-ratio method (LRM), and practical bump policies.
- **Fundamentos de Valoración** (course on asset-pricing fundamentals), **Module 4** — Black–Scholes via the heat equation: closed-form European call/put, replication (delta-hedging), analytical Greeks and call–put parity.
- **Fundamentos de Valoración** (course on asset-pricing fundamentals), **Module 5** — Monte Carlo fundamentals (LLN, CLT, confidence intervals, reproducibility) and the exact Black–Scholes step (Privault Prop. 5.15) reused from Assignment 3.

### Textbooks

- **Hull, J. C.** (2021). *Options, Futures, and Other Derivatives*, 11th edition. Pearson. Ch. 19 ("The Greek Letters"), closed-form Greeks and the canonical worked example used as the regression anchor in test #1.
- **Glasserman, P.** (2004). *Monte Carlo Methods in Financial Engineering*. Springer. Ch. 7 ("Estimating Sensitivities"): Sec. 7.1 (finite differences, bias-variance trade-off, Table 7.1), Sec. 7.2 (pathwise derivative estimates), Sec. 7.3 (likelihood-ratio method).

### Tooling

- `pytest`: <https://docs.pytest.org/en/stable/>.
- [Main README](../README.md).
