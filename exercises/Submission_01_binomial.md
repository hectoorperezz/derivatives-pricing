# Assignment 1: Binomial Pricing for European Call and Put

## Objective

Implement pricing of **European call** and **European put** options using a **binomial tree model**. Your solution must follow the modular architecture described in the [main README](../../README.md) and expose the required functions through the single public interface `hesperides/api.py`.

---

## API Contract

Tests (public and private) will **only** import:

```python
import hesperides.api as hapi
```

You must implement the following facade function in `hesperides/api.py` with the **exact signature** specified below. The argument `call` must be a boolean: `True` for a call option, `False` for a put option.

### Binomial European option (call or put)

```python
def get_price_binomial_european(
    St: float,
    K: float,
    T: int,
    R: float,
    u: float,
    d: float,
    call: bool,
) -> float:
    """
    Price a European call or put option using the binomial model.

    Parameters
    ----------
    St : float
        Spot price of the underlying at time t.
    K : float
        Strike price.
    T : int
        Number of time steps to maturity.
    R : float
        Risk-free rate (per period).
    u : float
        Up factor.
    d : float
        Down factor.
    call : bool
        If True, price a call option; if False, price a put option.

    Returns
    -------
    float
        Option price at time t.
    """
    ...
```

---

## Requirements

- Do not forget to follow the modular architecture and the single public interface rules stated in the [main README](../../README.md).

- For this assignment, note that for a fixed time you do not need an explicit Python loop over tree nodes to perform backward induction. **This can be implemented with NumPy array operations.**
- For this particular case, the risk-free rate is a constant. This will not always be the case, so you should not hardcode it. It is highly recommended to implement a **FlatDiscountCurve** class (or similar) in the module where all the curves are defined.



---

## Submission Checklist

Before submitting, verify the instructions in the [main README](../../README.md).

In addition, you must verify that the following tests, to be included in your library, pass:

- [test_binomial_european.py](../../public_tests/test_binomial_european.py) 

## References

- [Main project README](../../README.md)

