Quickstart
==========

All interaction with the library goes through :mod:`derivatives_pricing.api`.

Price a European option with the binomial tree
----------------------------------------------

.. code-block:: python

   import derivatives_pricing.api as pricing

   price = pricing.get_price_binomial_european(
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

   import derivatives_pricing.api as pricing

   european = pricing.get_price_bs_european(
       St=100.0,
       K=100.0,
       T=1.0,
       r=0.05,
       sigma=0.20,
       call=True,
       engine="analytical",
   )

   asian_mc = pricing.get_price_bs_geometric_asian(
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

Price cost-of-carry options
---------------------------

Dividend-paying stocks, FX options and futures options all reuse the same
Black--Scholes model with a continuous yield ``q``.

.. code-block:: python

   import derivatives_pricing.api as pricing

   dividend_call = pricing.get_price_bs_european_dividend(
       St=100.0,
       K=100.0,
       T=1.0,
       r=0.05,
       sigma=0.20,
       call=True,
       q=0.02,
   )

   fx_call = pricing.get_price_fx_option(
       St=1.10,
       K=1.05,
       T=1.0,
       r_d=0.03,
       r_f=0.01,
       sigma=0.18,
       call=True,
   )

   future_call = pricing.get_price_future_option(
       F0=100.0,
       K=98.0,
       T=0.75,
       r=0.04,
       sigma=0.20,
       call=True,
   )

   print(f"Dividend call: {dividend_call:.4f}")
   print(f"FX call: {fx_call:.4f}")
   print(f"Future call: {future_call:.4f}")

Solve the heat equation
-----------------------

The one-dimensional heat equation can be solved directly with explicit or
implicit finite differences.

.. code-block:: python

   import numpy as np
   import derivatives_pricing.api as pricing

   x_grid, u_T = pricing.solve_heat_equation(
       initial_condition=lambda x: np.sin(np.pi * x),
       kappa=0.5,
       M=1.0,
       T=0.02,
       n_x=40,
       n_t=400,
       scheme="explicit",
   )

   print(f"Final value at the midpoint: {u_T[len(u_T) // 2]:.4f}")

Price Black--Scholes through heat
---------------------------------

European calls and puts can also be priced by transforming Black--Scholes into
the heat equation and solving the resulting PDE.

.. code-block:: python

   import derivatives_pricing.api as pricing

   heat_call = pricing.get_price_bs_european_heat(
       St=100.0,
       K=100.0,
       T=1.0,
       r=0.03,
       sigma=0.20,
       call=True,
       scheme="implicit",
   )

   closed_call = pricing.get_price_bs_european(
       St=100.0,
       K=100.0,
       T=1.0,
       r=0.03,
       sigma=0.20,
       call=True,
   )

   print(f"Heat PDE: {heat_call:.4f}")
   print(f"Closed form: {closed_call:.4f}")

Compute Black--Scholes Greeks
-----------------------------

European Black--Scholes Greeks are available with closed-form formulas or with
finite-difference bump-and-reprice. Finite differences can wrap either the
analytical pricer or the Monte Carlo pricer.

.. code-block:: python

   import derivatives_pricing.api as pricing

   delta = pricing.get_greek_bs_european(
       St=100.0,
       K=100.0,
       T=1.0,
       r=0.05,
       sigma=0.20,
       call=True,
       greek="delta",
       greek_engine="analytical",
   )

   rho_fd = pricing.get_greek_bs_european(
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
   import derivatives_pricing.api as pricing

   # surface[k, t] = call price with strike k and expiry t
   surface = np.array([
       [12.0, 14.0],
       [ 7.0,  9.5],
       [ 3.5,  5.5],
       [ 1.0,  2.5],
   ])
   strikes = np.array([90.0, 100.0, 110.0, 120.0])

   verticals = pricing.compute_static_arbitrage_quantity(
       surface, strikes=strikes, quantity="vertical",
   )
   butterflies = pricing.compute_static_arbitrage_quantity(
       surface, strikes=strikes, quantity="butterfly",
   )

Any negative value in ``butterflies`` (negative implied density) or a
mis-oriented vertical spread signals a no-arbitrage violation.
