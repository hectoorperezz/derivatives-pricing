# Assignment 5: Dividends, FX and futures under Black–Scholes (cost of carry)

## Goal

Extend the Black–Scholes model of Assignment 3 with a continuous **dividend yield** $q$ and use the resulting **cost-of-carry** formulation — a risk-neutral drift $r - q$ in place of $r$ — to price three families of European options:

1. options on a **stock paying a continuous dividend yield** $q$;
2. **FX options** (Garman–Kohlhagen), where the foreign rate plays the role of the dividend yield ($q = r_f$);
3. options on a **future** (Black-76), where the future is driftless under $\mathbb{Q}$ ($q = r$, i.e. zero carry).

The three are a single idea seen from three angles (*Fundamentos de Valoración*, Module 9): an asset that pays a continuous income stream grows, under the risk-neutral measure, at the **drift $r - q$** rather than at $r$, where $q$ is whatever the holder earns *outside* price appreciation — a dividend yield, the foreign rate, or (for a future, whose mark-to-market absorbs the discount) the full $r$. **Discounting is unchanged: it always uses the risk-free rate $r$ (resp. the domestic rate $r_d$).**

You must reuse the European option product, the Black–Scholes model, and both engines (analytical and Monte Carlo) from Assignment 3. The change is **local**: a single new parameter $q$ on the model, threaded through the drift and the closed-form price. With $q = 0$ everything must reduce **exactly** to Assignment 3.

The solution must follow the modular architecture in the [README](../README.md) and expose entry points only through the `hesperides/api.py` *facade*.

---

## Theory (follow the Module 9 notes; reference them for the explicit formulas)

This assignment deliberately reproduces almost no algebra. The closed-form prices, the put–call parities and the change-of-variable identities are all derived in the **Module 9 notes**, and you should read them there rather than re-derive them here. Below we keep only the few formulas needed to see *why the change in code is a one-line change*, and point to the notes for the rest.

### The one structural change: the risk-neutral drift

Under $\mathbb{Q}$, an asset paying a continuous yield $q$ has dynamics

$$
dS_t = (r - q)\,S_t\,dt + \sigma\,S_t\,dW_t^{\mathbb{Q}}.
$$

This single substitution $r \to r - q$ in the drift *is* the assignment. From it follow the dividend-adjusted Black–Scholes PDE (Module 9, *Prop. 16.6*), the risk-neutral valuation formula (*Prop. 16.7*), and the closed-form European call/put (Module 4, with the drift $r-q$ and discounting kept at $r$). **Do not copy those formulas here — reference the notes.** The explicit $d_\pm$ and the **dividend put–call parity** likewise live in the notes; parity is restated *once*, as an acceptance test, under *Numerical consistency* below.

The one identity worth keeping in view — because the code and the tests use it directly — is the **reduction formula** (Module 9, *Prop. 16.9*): the price with yield $q$ equals the dividend-free price at a discounted spot,

$$
F^{q}(t, s) = F^{0}\!\big(t,\; s\,e^{-q(T-t)}\big).
$$

This is why no formula has to be reprogrammed: the dividend, FX and futures prices are the Assignment 3 price evaluated at a shifted spot / with a shifted drift.

### The three instances of $q$

- **Dividends.** $q$ is the continuous dividend yield. This is the base case (Module 9, §16.2).
- **FX (Garman–Kohlhagen).** For an exchange rate $X_t$ quoted as *domestic per unit foreign*, holding the foreign currency earns $r_f$, so $X$ behaves like a stock with $q = r_f$, priced under the **domestic** measure and discounted at $r_d$ (Module 9, FX section; the dividend analogy is made explicit there). Concretely, it is the cost-of-carry model with the substitution $q \leftrightarrow r_f$, $r \leftrightarrow r_d$.
- **Futures (Black-76).** A future is, in the language of the notes, an asset that is "all dividend and no spot": its mark-to-market pays out the change in its own quote continuously, and the futures price is a $\mathbb{Q}$-martingale (Module 9, *Prop. 17.6*),

  $$
  dF_t = \sigma\,F_t\,dW_t^{\mathbb{Q}}.
  $$

  A driftless underlying is exactly the cost-of-carry model with **zero carry**, $q = r$. Discounting still uses $r$, and the result is the **Black-76** formula (Module 9, *Black-76 exercise*) — no new model, only $q = r$. (See the notes for the explicit Black-76 closed form.)

### In what sense is the Monte Carlo engine "necessary"?

These are vanilla European options with known closed forms, so Monte Carlo is **not** needed to obtain the price. It is required for two different reasons, and the spec treats it as such:

1. **Independent cross-check.** A simulation that knows nothing about the closed form, agreeing with it to within a few standard errors, is genuine evidence that both are right. This is the *Analytical vs Monte Carlo* property below.
2. **A test of architectural locality.** The only thing that changes from Assignment 3 in the Monte Carlo path is the log-drift of the exact GBM step, $\int r \to \int (r - q)$ (and $q = r$, i.e. *zero* drift, for a future). If one engine prices all three families after that single change — no special-casing — the abstraction is correct.

So Monte Carlo is "necessary" here in the sense of *validation and architecture*, not as the only way to compute the number.

---

## API contract

Tests (public and private) will **only** import:

```python
import hesperides.api as hapi
```

Implement these *facade* functions in `hesperides/api.py` with the **exact** signatures below.

### Dividend-paying European option

```python
def get_price_bs_european_dividend(
    St: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    call: bool,
    q: float = 0.0,
    engine: str = "analytical",
    n_paths: int | None = None,
    seed: int | None = None,
) -> float:
    """
    Price a European option on a stock paying a continuous dividend yield q.

    Risk-neutral dynamics dS = (r - q) S dt + sigma S dW (Module 9);
    discounting still uses r. With q = 0 this recovers Assignment 3.

    Parameters
    ----------
    St, K, T, r, sigma, call, engine, n_paths, seed
        As in ``get_price_bs_european`` (Assignment 3).
    q : float, optional
        Continuous dividend yield. Default 0.0 (recovers Assignment 3).

    Returns
    -------
    float
        Option price at valuation date.
    """
    ...
```

### FX option (Garman–Kohlhagen)

```python
def get_price_fx_option(
    St: float,
    K: float,
    T: float,
    r_d: float,
    r_f: float,
    sigma: float,
    call: bool,
    engine: str = "analytical",
    n_paths: int | None = None,
    seed: int | None = None,
) -> float:
    """
    Price a European FX option under the Garman–Kohlhagen model.

    St is the FX spot (domestic per unit foreign); r_d and r_f are the
    domestic and foreign continuously compounded rates; the price is returned
    in domestic currency. Internally this is the cost-of-carry model with
    q = r_f and r = r_d.

    Returns
    -------
    float
        Option price at valuation date, in domestic currency.
    """
    ...
```

### Option on a future (Black-76)

```python
def get_price_future_option(
    F0: float,
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
    Price a European option on a future under the Black-76 model.

    F0 is the current future price. Under Q the future is driftless,
    dF = sigma F dW, i.e. the cost-of-carry model with zero carry (q = r);
    discounting uses r. With these inputs the price is the Black-76 value
    e^{-rT} (F0 N(d_+) - K N(d_-)) for a call. No separate "futures model":
    reuse the same Black–Scholes model with q = r.

    Returns
    -------
    float
        Option price at valuation date.
    """
    ...
```

`engine` must accept exactly `"analytical"` and `"mc"`; any other value raises `ValueError`. If `engine="mc"`, `n_paths` is required and passing `None` raises `ValueError`. Non-positive `sigma`/`K`/`St` (resp. `F0`) and negative `T` raise `ValueError`. The dividend yield `q` and the rates `r`, `r_d`, `r_f` may be any sign (a negative foreign rate, or a negative discount rate, is legitimate).

---

## Requirements

### Architecture

- Follow the modular architecture and **single public interface** rule in the [main README](../README.md).
- Add the dividend yield $q$ as a parameter of the **Black–Scholes model**, not of the engines. The model exposes the drift $r - q$ (the cost of carry); the engines read $q$ from the model. Do **not** add a separate "FX model", "dividend model" or "futures model": all three facades must be priced by the **same** Black–Scholes model — FX with $q = r_f$ and a domestic discount curve, and the future with $q = r$ (zero carry).
- **Discounting stays in the discount curve** and always uses $r$ (resp. $r_d$). Do not let $q$ leak into the discount factor; do not *hardcode* $e^{-rT}$ or $e^{-qT}$ inside the engines — the discount factor comes from the curve and $e^{-qT}$ comes from the model's integrated yield.
- $q = 0$ must reproduce Assignment 3 **bit-for-bit** (no new code path for the dividend-free case).

### Vectorization

- Monte Carlo simulation and *payoff* must use NumPy (no Python loops over paths). The exact-step simulation only changes the log-drift from $\int r$ to $\int (r-q)$ (which collapses to zero drift for the future, $q = r$).

### Reproducibility

- Monte Carlo must be reproducible via `seed`, using `np.random.default_rng(seed)` (never the legacy global RNG), as in Assignment 3.

### Numerical consistency (graded properties)

Your closed-form and Monte Carlo prices must satisfy, within the appropriate tolerance:

- **Recovery**: `get_price_bs_european_dividend(..., q=0.0)` equals `get_price_bs_european(...)`.
- **Dividend put–call parity**: $C - P = S\,e^{-qT} - K\,e^{-rT}$ (Module 9 / Module 4).
- **Reduction formula**: the dividend price equals the dividend-free price at spot $S\,e^{-qT}$.
- **FX symmetry**: the same FX option priced as a stock-with-dividend ($q = r_f$, curve rate $r_d$) and through `get_price_fx_option` must agree.
- **Futures symmetry**: `get_price_future_option(F0, ...)` must equal the dividend model with spot `F0` and $q = r$; equivalently, the **Black-76 put–call parity** $C - P = e^{-rT}\,(F_0 - K)$ holds (it is the dividend parity with $q = r$).
- **Analytical vs Monte Carlo** agreement within a few standard errors, for all three families.

---

## Optional extension*: discrete dividends

> Marked with an asterisk: **not required**. Offered for students who want to go further; grading targets only the continuous-yield, FX and futures facades above.

The notes value **known discrete cash dividends** $\delta_1, \dots, \delta_K$ paid at dates $0 < T_1 < \dots < T_K < T$ **exactly**, by no-arbitrage: at each date the *ex-dividend* jump of the underlying is

$$
S_{T_n} = S_{T_n^-} - \delta_n
$$

(Module 9, *Prop. 16.1*), and the option is priced by a **backward recursion** that runs the standard Black–Scholes PDE between dividend dates and applies the jump $s \mapsto s - \delta_n$ at each $T_n$ (Module 9, §16.1.4–16.1.5). The option does **not** collect the dividend; only the state $S$ jumps.

The **escrowed-dividend model** is the classic practitioner *approximation* to that exact recursion, and the name is worth spelling out: the present value of the known dividends is treated as a riskless amount held *in escrow* — carved out of the diffusing part of the spot — so you subtract it from today's spot and price the residual with the plain (dividend-free) model,

$$
\widetilde{S}_0 = S_0 - \sum_{T_n \le T} \delta_n\,e^{-r T_n},
\qquad
\text{price} \approx F^{0}\!\big(0,\, \widetilde{S}_0\big).
$$

It is *only* an approximation: the true dynamics jump (Prop. 16.1), whereas the escrowed spot shifts deterministically and lets the whole residual diffuse; the two agree only in the small-dividend limit. Implement it on top of the dividend-free model, and (optionally) check it against the exact jump recursion as the benchmark. Expose it through a separate optional entry point; do not change the required signatures above.

---

## Tests with `pytest`

As in Assignments 3 and 4, **no public tests are provided**. Designing and writing the test suite is part of the spec, and tests are a deliverable on par with library code. Include your tests in the `.whl`.

- Tests in `tests/` per `pytest` conventions; `pytest` as a *dev* dependency in `pyproject.toml`.
- Compare floats with `pytest.approx`; parametrize with `@pytest.mark.parametrize`; contract errors with `pytest.raises(match=...)`.

### Minimum coverage

No fixed test count; you must at least cover:

- **Recovery**: `q = 0` reproduces the Assignment 3 European price (call and put).
- **Closed-form regression** for the dividend price against a hand-computed value, call and put.
- **Dividend put–call parity** $C - P = S e^{-qT} - K e^{-rT}$.
- **Reduction formula** equivalence.
- **FX**: `get_price_fx_option` equals the dividend model with $q = r_f$ and domestic discounting; a sanity check with $r_f = 0$ reduces to the plain stock case.
- **Futures (Black-76)**: closed-form regression against a hand-computed value (call and put); the **Black-76 put–call parity** $C - P = e^{-rT}(F_0 - K)$; and `get_price_future_option(F0, ...)` equals the dividend model with spot `F0` and $q = r$ (with $r = 0$ it reduces to the plain undiscounted European price at spot `F0`).
- **Analytical vs Monte Carlo** for the dividend and the futures option, fixed `seed`, sensible tolerance.
- **Validation**: each `ValueError` branch in the API contract.

---

## Submission checklist

Before submitting, check the general instructions in the [main README](../README.md). Submissions that cannot be installed and run will not be graded. Tests from earlier assignments may still be evaluated, and Assignment 3 prices must remain unchanged.

---

## References

### Course modules

- **Fundamentos de Valoración** (asset-pricing fundamentals), **Module 9** — dividends, futures and FX as variations on the cost of carry. The notes contain the explicit formulas this assignment references: the dividend-adjusted Black–Scholes PDE (*Prop. 16.6*), risk-neutral valuation (*Prop. 16.7*), the reduction formula $F^q(t,s) = F^0(t, s\,e^{-q(T-t)})$ (*Prop. 16.9*), the discrete-dividend jump condition $S_{T_n} = S_{T_n^-} - \delta_n$ (*Prop. 16.1*), the foreign-account-as-asset argument that makes $r_f$ act as a dividend yield (FX / Garman–Kohlhagen section), the futures price as a $\mathbb{Q}$-martingale (*Prop. 17.6*), and the **Black-76** option-on-future formula (Black-76 exercise).
- **Fundamentos de Valoración** (asset-pricing fundamentals), **Module 4** — closed-form European call/put under Black–Scholes and the put–call parity (reused with the cost-of-carry adjustment).

### Tooling

- `pytest`: <https://docs.pytest.org/en/stable/>.
- NumPy random (`Generator`): <https://numpy.org/doc/stable/reference/random/generator.html>.
- [Main README](../README.md).
