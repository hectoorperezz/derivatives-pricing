Quickstart
==========

All interaction with the library goes through :mod:`hesperides.api`.

Price a European option with the binomial tree
----------------------------------------------

.. code-block:: python

   import hesperides.api as hapi

   price = hapi.get_price_binomial_european(
       St=100.0,   # spot
       K=100.0,    # strike
       T=3,        # number of tree steps
       R=0.05,     # risk-free rate per period
       u=1.1,      # up move
       d=0.9,      # down move
       call=True,  # True for call, False for put
   )

   print(f"Price: {price:.4f}")

Price Black--Scholes options
----------------------------

European options and continuous geometric Asian options are available under
Black--Scholes with analytical and Monte Carlo engines.

.. code-block:: python

   import hesperides.api as hapi

   european = hapi.get_price_bs_european(
       St=100.0,
       K=100.0,
       T=1.0,
       r=0.05,
       sigma=0.20,
       call=True,
       engine="analytical",
   )

   asian_mc = hapi.get_price_bs_geometric_asian(
       St=100.0,
       K=100.0,
       T=1.0,
       r=0.05,
       sigma=0.20,
       call=True,
       engine="mc",
       n_paths=50_000,
       n_steps=252,
       seed=123,
   )

   print(f"European: {european:.4f}")
   print(f"Geometric Asian MC: {asian_mc:.4f}")

Compute Black--Scholes Greeks
-----------------------------

European Black--Scholes Greeks are available with closed-form formulas or with
finite-difference bump-and-reprice. Finite differences can wrap either the
analytical pricer or the Monte Carlo pricer.

.. code-block:: python

   import hesperides.api as hapi

   delta = hapi.get_greek_bs_european(
       St=100.0,
       K=100.0,
       T=1.0,
       r=0.05,
       sigma=0.20,
       call=True,
       greek="delta",
       greek_engine="analytical",
   )

   rho_fd = hapi.get_greek_bs_european(
       St=100.0,
       K=100.0,
       T=1.0,
       r=0.05,
       sigma=0.20,
       call=True,
       greek="rho",
       greek_engine="fd",
       engine="analytical",
   )

   print(f"Delta: {delta:.4f}")
   print(f"Rho by finite differences: {rho_fd:.4f}")

Detect static arbitrage on a call surface
-----------------------------------------

Given a grid of call prices, compute the Carr–Madan quantities (vertical
spreads, butterflies or calendars):

.. code-block:: python

   import numpy as np
   import hesperides.api as hapi

   # surface[k, t] = call price with strike k and expiry t
   surface = np.array([
       [12.0, 14.0],
       [ 7.0,  9.5],
       [ 3.5,  5.5],
       [ 1.0,  2.5],
   ])
   strikes = np.array([90.0, 100.0, 110.0, 120.0])

   verticals = hapi.compute_static_arbitrage_quantity(
       surface, strikes=strikes, quantity="vertical",
   )
   butterflies = hapi.compute_static_arbitrage_quantity(
       surface, strikes=strikes, quantity="butterfly",
   )

Any negative value in ``butterflies`` (negative implied density) or a
mis-oriented vertical spread signals a no-arbitrage violation.
