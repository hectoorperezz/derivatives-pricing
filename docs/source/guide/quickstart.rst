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
