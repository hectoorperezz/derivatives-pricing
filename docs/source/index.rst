Hesperides
==========

.. raw:: html

   <div class="hesperides-hero">
     <span class="hesperides-eyebrow"><span class="dot"></span>Universidad de las Hespérides · v0.4</span>
     <h1 class="hesperides-title">Hesperides</h1>
     <p class="hesperides-tagline">
       A Python library for <strong>derivatives pricing and Greeks</strong>.
       Modular architecture, a single stable public surface, and
       vectorized NumPy throughout.
     </p>
     <div class="hesperides-cta-row">
       <a class="hero-cta hero-cta--primary" href="guide/quickstart.html">
         Get started &rarr;
       </a>
       <a class="hero-cta hero-cta--ghost" href="api/index.html">
         API reference
       </a>
     </div>
   </div>

.. code-block:: python

   import hesperides.api as hapi

   price = hapi.get_price_bs_european(
       St=100.0, K=100.0, T=1.0, r=0.05,
       sigma=0.20, call=True,
   )

   delta = hapi.get_greek_bs_european(
       St=100.0, K=100.0, T=1.0, r=0.05,
       sigma=0.20, call=True, greek="delta",
   )

Explore
-------

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: Installation
      :link: guide/installation
      :link-type: doc

      Set up Python 3.13, install the wheel and prepare the docs environment.

   .. grid-item-card:: Quickstart
      :link: guide/quickstart
      :link-type: doc

      Price European and geometric Asian options, and compute Greeks.

   .. grid-item-card:: Architecture
      :link: guide/architecture
      :link-type: doc

      Contracts, market, models, engines, Greeks, pricers — and why.

   .. grid-item-card:: Theory
      :link: guide/theory
      :link-type: doc

      Formulas: binomial pricing, Black--Scholes, Greeks and no-arbitrage.

   .. grid-item-card:: Public API
      :link: api/public
      :link-type: doc

      Functions in ``hesperides.api``: the single stable surface.

   .. grid-item-card:: Market & Models
      :link: api/market
      :link-type: doc

      Market data, curves and dynamics under the pricing measure.

Design principles
-----------------

.. grid:: 1 1 2 2
   :gutter: 3

   .. grid-item::

      **One API**

      All functionality flows through :mod:`hesperides.api`. The rest of the
      package is internal and may be refactored without breaking consumers.

   .. grid-item::

      **Layer separation**

      *Contracts* describe the payoff, *models* the dynamics, *engines* the
      algorithm, *pricers* the orchestration. No cross-coupling.

   .. grid-item::

      **Vectorization first**

      NumPy operations with explicit ``dtype`` and broadcasting. Python loops
      are the exception, not the rule.

   .. grid-item::

      **Reproducibility**

      Monte Carlo always seeded. Public tests in the repo, private tests for
      the grade.

.. toctree::
   :hidden:
   :caption: Guide

   guide/installation
   guide/quickstart
   guide/architecture
   guide/theory

.. toctree::
   :hidden:
   :caption: Reference

   api/index
