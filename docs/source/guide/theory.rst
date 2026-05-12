Mathematical foundations
========================

A derivatives pricing library is, at heart, an answer to a single question:
**what is a fair price for a contingent claim?** The course teaches that this
question rests on three pillars — **no-arbitrage**, **replication** and
**martingale measures** — and that everything else (Black–Scholes, Greeks,
smile, incomplete markets) is a technical extension of these ideas.

The fair price of a derivative does not depend on what we believe the
underlying will do; it depends on what *prevents* riskless profit. If a
portfolio of bonds and stocks reproduces the derivative's payoff in every
state of the world, then by no-arbitrage the derivative must cost the same
as that portfolio today. In the binomial setting this replication argument is
constructive: the hedge is the solution of a :math:`2 \times 2` linear system,
and the resulting price coincides with a discounted expectation under a
synthetic probability measure :math:`\Q` — the *risk-neutral measure*. Under
:math:`\Q` discounted prices are martingales, and that is precisely what
guarantees the absence of arbitrage.

This page captures only the formulas the library actually executes — the
no-arbitrage condition, the risk-neutral probabilities and the backward
induction that powers
:class:`~hesperides.engines.binomial_engine.BinomialTreeEngine`, plus the
static-arbitrage diagnostics of Carr–Madan exposed through
:func:`~hesperides.api.compute_static_arbitrage_quantity`. The notation
follows the course notes.

Notation
--------

.. admonition:: Notation reference
   :class: notbox

   - :math:`t \in \{0, 1, \ldots, T\}` — discrete time steps.
   - :math:`B_t` — risk-free bond: :math:`B_0 = 1`, :math:`B_{t+1} = (1+R)\, B_t`.
   - :math:`S_t` — underlying: :math:`S_0 = s`, :math:`S_{t+1} = S_t\, Z_t` with :math:`Z_t \in \{u, d\}` i.i.d.
   - :math:`h = (x, y)` — portfolio: :math:`x` bonds, :math:`y` units of underlying.
   - :math:`V_t^h = x\, B_t + y\, S_t` — portfolio value.
   - :math:`\payoff(S_T)` — terminal payoff. European call: :math:`\payoff(S_T) = \pos{S_T - K}`.
   - :math:`\Q \sim \P` — risk-neutral measure, equivalent to the real one.

Binomial model
--------------

.. admonition:: No-arbitrage condition
   :class: defbox

   The model is arbitrage-free if and only if

   .. math::

      d \;<\; 1 + R \;<\; u.

   The library validates this condition before building the tree.

.. admonition:: Risk-neutral probabilities
   :class: defbox

   .. math::

      q_u \;=\; \frac{1 + R - d}{u - d},
      \qquad
      q_d \;=\; 1 - q_u \;=\; \frac{u - (1 + R)}{u - d}.

   Defined so that :math:`\E^{\Q}[Z] = 1 + R`: under :math:`\Q` the underlying
   yields the same as the bond.

.. admonition:: Backward-induction pricing
   :class: defbox

   Starting from :math:`X = \payoff(S_T)` at the leaves of the tree,

   .. math::

      \Price{t}\![X] \;=\; \frac{1}{1+R}\, \E^{\Q}\!\left[\Price{t+1}\![X] \,\middle|\, \Filt_t\right].

   Iterating for :math:`T` steps yields :math:`\Price{0}\![X]`. This is exactly
   what :class:`~hesperides.engines.binomial_engine.BinomialTreeEngine` does.

The price **does not depend on the real probability** :math:`p`, only on
:math:`u`, :math:`d` and :math:`R`. Every derivative is replicable and
:math:`\Q` is unique.

Static no-arbitrage on call surfaces
------------------------------------

Given a discrete grid :math:`C_{i,j} = C(K_i, T_j)`, the Carr–Madan
quantities detect no-arbitrage violations.

.. admonition:: Vertical spread (normalized)
   :class: defbox

   Must lie in :math:`[0, 1]`.

   .. math::

      \overline{Q}_{i,j} \;=\; \frac{C_{i-1,j} - C_{i,j}}{K_i - K_{i-1}}.

.. admonition:: Butterfly spread
   :class: defbox

   Discrete Breeden–Litzenberger implied density. Must be :math:`\geq 0`;
   a negative value signals a negative implied density around :math:`K_i`.

   .. math::

      \mathrm{BS}_{i,j} \;=\; C_{i-1,j}
      \,-\, \frac{K_{i+1} - K_{i-1}}{K_{i+1} - K_i}\, C_{i,j}
      \,+\, \frac{K_i - K_{i-1}}{K_{i+1} - K_i}\, C_{i+1,j}.

.. admonition:: Calendar spread
   :class: defbox

   Must be :math:`\geq 0`.

   .. math::

      \mathrm{CS}_{i,j} \;=\; C_{i,j+1} - C_{i,j}.

The three quantities are exposed to users through
:func:`~hesperides.api.compute_static_arbitrage_quantity`.
