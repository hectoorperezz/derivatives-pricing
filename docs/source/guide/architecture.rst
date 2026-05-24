Architecture
============

The library follows a **strict separation of concerns**. Each subpackage has a
single responsibility; clients should only import :mod:`hesperides.api`.

.. code-block:: text

   hesperides/
   ├── api.py            # ← single public surface
   ├── contracts/        # what is being priced (European, Asian, ...)
   ├── market/           # market data (spot, curves, surfaces)
   ├── models/           # underlying dynamics (Binomial, Black-Scholes, ...)
   ├── engines/          # numerical algorithm (tree, analytical, MC, ...)
   └── pricers/          # orchestration: contract + model + market + engine

Layers
------

:py:mod:`hesperides.contracts`
    Describe the payoff. Purely declarative: strike, expiry, type (call/put),
    barrier, etc. They know nothing about models or market.

:py:mod:`hesperides.market`
    Observable or calibrated data: spot, discount curve, price surfaces. The
    separation from models allows recalibration without touching the rest.

:py:mod:`hesperides.models`
    Dynamics of the underlying under the pricing measure (Q). For example, the
    binomial tree receives :math:`u`, :math:`d`; Black--Scholes receives
    :math:`\sigma`.

:py:mod:`hesperides.engines`
    Implement the numerical algorithm that walks the model and applies the
    contract's payoff (tree rollback, MC, PDE integration, ...).

:py:mod:`hesperides.pricers`
    Glue together the four pieces above and return the price. The only layer
    that knows about all the others.

Why a single ``api``?
---------------------

The course's grading system installs the ``.whl`` into a clean environment and
can only use ``import hesperides.api as hapi``. The rest of the package is
internal and **can be refactored freely** as long as the signatures of the
functions in ``api.py`` do not change.

Performance rules
-----------------

- Vectorized NumPy operations rather than Python loops.
- Explicit ``dtype`` whenever possible.
- Monte Carlo: vectorization plus reproducibility through seeds.

See the `NumPy broadcasting guide
<https://numpy.org/doc/stable/user/basics.broadcasting.html>`_ for the
supported patterns.
