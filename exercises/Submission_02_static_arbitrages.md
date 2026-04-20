# Assignment 2: Static arbitrage checks on call surfaces

## Goal

Read Carr and Madan (2005) on **static arbitrage** and implement, in the Hesperides library, **numerical checks** on a **discrete call-price surface** $C_{i,j}$ (strikes $\times$ maturities) that detect the usual **vertical**, **butterfly**, and **calendar** spread conditions. Your solution must follow the modular architecture in the [main README](../README.md) and expose the required entry points through the single public interface `hesperides/api.py`.


---

## API Contract

Tests (public and private) will **only** import:

```python
import hesperides.api as hapi
```

Implement the following **facade function** in `hesperides/api.py` with the **exact signature** below. It must compute the same Carr–Madan quantities as the paper: normalized vertical spreads ($\bar Q_{i,j}$), **butterfly** values $\mathrm{BS}_{i,j}$, and **calendar** spreads $\mathrm{CS}_{i,j}=C_{i,j+1}-C_{i,j}$. Use a single entry point and dispatch internally on `quantity`.

Use **NumPy** `ndarray` inputs. **Rows = strikes**, **columns = expiries**; for vertical and butterfly modes, `strikes` must be **strictly increasing**.

```python
def compute_static_arbitrage_quantity(
    surface: np.ndarray,
    strikes: np.ndarray | None = None,
    quantity: str = "vertical",
) -> np.ndarray:
    """
    Carr–Madan static-arbitrage spread grids on a call surface C_{i,j}.

    Parameters
    ----------
    surface : ndarray, shape (nK, nT)
        Call prices by strike (row) and expiry (column).
    strikes : ndarray, shape (nK,) or None
        Strictly increasing strikes. Required for ``quantity`` ``'vertical'`` and
        ``'butterfly'``; ignored for ``'calendar'``.
    quantity : {'vertical', 'butterfly', 'calendar'}, optional
        Which spread grid to return.

    Returns
    -------
    ndarray
        * ``'vertical'``: normalized vertical call spreads, shape (nK-1, nT).
          For K_0 < ... < K_{nK-1} and i = 1, ..., nK-1,

          Q_{i,j} = (C_{i-1,j} - C_{i,j}) / (K_i - K_{i-1}).

        * ``'butterfly'``: interior butterfly values (at least three strikes),
          shape (nK-2, nT), matching Carr–Madan’s construction after equation (1).

        * ``'calendar'``: calendar spreads across consecutive expiries,
          shape (nK, nT-1),

          CS_{i,j} = C_{i,j+1} - C_{i,j}.
    """
    ...
```

The string `quantity` must accept: `"vertical"`, `"butterfly"`, or `"calendar"`. It must raise a `ValueError` if an invalid value is provided.

---

## Requirements

- Follow the modular architecture and the **single public interface** rules in the [main README](../README.md): implement helpers in internal modules if you wish, but expose **only** `compute_static_arbitrage_quantity` from `hesperides/api.py` so tests only use `import hesperides.api as hapi`.

- **Vectorization:** implement the spread grids with **NumPy** array operations (broadcasting, `np.diff`, etc.). Avoid Python loops over strikes or maturities.

- **Consistency with the paper:** formulas must match Carr–Madan (2005), equations (1) and the butterfly construction following (1), and calendar spreads as in their equation (4). 

- Although it may be adjusted in the future, this functionality should be placed in the part of the library that covers `Markets`, as indicated in the `README.md`.


---

## Submission Checklist

Before submitting, verify the instructions in the [main README](../README.md).

In addition, ensure that the following **public** tests, included in the course repository, pass in your library:

- [test_static_arbitrage.py](../public_tests/test_static_arbitrage.py)

Note: the provided surface is extended in the Carr–Madan sense, using the $K=0$ and $T=0$ boundary values on the discrete grid.

---

## References

- Carr, P., and Madan, D. (2005). A note on sufficient conditions for no arbitrage. *Finance Research Letters*, 2(3–4), 125–130. 

- [Main project README](../README.md)
