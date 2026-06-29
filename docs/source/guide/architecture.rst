Architecture
============

The library follows a **strict separation of concerns**. Each subpackage has a
single responsibility; clients should only import :mod:`derivatives_pricing.api`.

.. code-block:: text

   derivatives_pricing/
   ├── api.py            # ← single public surface
   ├── contracts/        # what is being priced (European, Asian, ...)
   ├── market/           # market data (spot, curves, surfaces)
   ├── models/           # underlying dynamics (Binomial, Black-Scholes, ...)
   ├── engines/          # numerical algorithm (tree, analytical, MC, ...)
   ├── greeks/           # sensitivities (analytical, finite differences)
   └── pricers/          # orchestration: contract + model + market + engine

Layers
------

:py:mod:`derivatives_pricing.contracts`
    Describe the payoff. Purely declarative: strike, expiry, type (call/put),
    barrier, etc. They know nothing about models or market.

:py:mod:`derivatives_pricing.market`
    Observable or calibrated data: spot, discount curve, price surfaces. The
    separation from models allows recalibration without touching the rest.

:py:mod:`derivatives_pricing.models`
    Dynamics of the underlying under the pricing measure (Q). For example, the
    binomial tree receives :math:`u`, :math:`d`; Black--Scholes receives
    :math:`\sigma` and the continuous yield :math:`q`.

:py:mod:`derivatives_pricing.engines`
    Implement the numerical algorithm that walks the model and applies the
    contract's payoff (tree rollback, MC, PDE integration, ...).

:py:mod:`derivatives_pricing.greeks`
    Compute sensitivities of European Black--Scholes prices. Analytical Greeks
    use closed-form derivatives; finite-difference Greeks bump inputs and
    reuse the existing pricing engines.

:py:mod:`derivatives_pricing.pricers`
    Glue together the four pieces above and return the price. The only layer
    that knows about all the others.

Why a single ``api``?
---------------------

The facade keeps the public interface small and stable:
``import derivatives_pricing.api as pricing``. The rest of the package is
internal and **can be refactored freely** as long as the functions in
``api.py`` keep their documented behaviour.

Performance rules
-----------------

- Vectorized NumPy operations rather than Python loops.
- Explicit ``dtype`` whenever possible.
- Monte Carlo: vectorization plus reproducibility through seeds.

See the `NumPy broadcasting guide
<https://numpy.org/doc/stable/user/basics.broadcasting.html>`_ for the
supported patterns.
