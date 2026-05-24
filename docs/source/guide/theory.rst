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
:class:`~hesperides.engines.binomial_engine.BinomialTreeEngine`, the
Black--Scholes closed forms and Monte Carlo simulation used by
:class:`~hesperides.engines.bs_analytical_engine.BlackScholesAnalyticalEngine`
and
:class:`~hesperides.engines.bs_monte_carlo_engine.BlackScholesMonteCarloEngine`,
plus the static-arbitrage diagnostics of Carr–Madan exposed through
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

Black--Scholes model
--------------------

In continuous time, Hesperides uses the Black--Scholes model under the
risk-neutral measure :math:`\Q`. The market provides the spot and discount
curve; :class:`~hesperides.models.black_scholes.BlackScholesModel`
parameterizes the diffusion with the annualized volatility :math:`\sigma`.

.. admonition:: Risk-neutral dynamics
   :class: defbox

   .. math::

      \dd S_t \;=\; r S_t \dt + \sigma S_t \dW_t^{\Q}.

   Hence, for :math:`Z \sim \normal{0}{1}`,

   .. math::

      S_T \;=\; S_0
      \exp\!\left(\left(r - \frac{1}{2}\sigma^2\right)T
      + \sigma \sqrt{T}\, Z\right).

   This exact lognormal transition is used by the Monte Carlo engine; no
   Euler discretization is needed for European terminal values.

.. admonition:: European Black--Scholes formula
   :class: defbox

   For :math:`\tau = T`, no dividends and

   .. math::

      d_1 \;=\;
      \frac{\log(S_0/K) + \left(r + \frac{1}{2}\sigma^2\right)\tau}
           {\sigma\sqrt{\tau}},
      \qquad
      d_2 \;=\; d_1 - \sigma\sqrt{\tau},

   the analytical engine returns

   .. math::

      C_0 \;=\; S_0 N(d_1) - K e^{-r\tau} N(d_2),

   .. math::

      P_0 \;=\; K e^{-r\tau} N(-d_2) - S_0 N(-d_1).

   The discount factor is obtained from
   :class:`~hesperides.market.curves.FlatDiscountCurve` with
   ``compounding="continuous"``.

.. admonition:: Geometric Asian average
   :class: defbox

   The continuous geometric average is

   .. math::

      G_T \;=\;
      \exp\!\left(\frac{1}{T}\int_0^T \log S_u\,\dd u\right).

   Under Black--Scholes,

   .. math::

      \log G_T \;\sim\;
      \normal{
         \log S_0 + \left(r - \frac{1}{2}\sigma^2\right)\frac{T}{2}
      }{
         \frac{\sigma^2 T}{3}
      }.

   Therefore :math:`G_T` is lognormal and admits a closed-form call and put
   price.

.. admonition:: Geometric Asian closed form
   :class: defbox

   Let

   .. math::

      m \;=\; \log S_0 + \left(r - \frac{1}{2}\sigma^2\right)\frac{T}{2},
      \qquad
      v \;=\; \frac{\sigma^2 T}{3},
      \qquad
      \overline{G} \;=\; e^{m + v/2}.

   With

   .. math::

      a_1 \;=\; \frac{m - \log K + v}{\sqrt{v}},
      \qquad
      a_2 \;=\; a_1 - \sqrt{v},

   the analytical geometric Asian prices are

   .. math::

      C_0^G \;=\; e^{-rT}\left(\overline{G}N(a_1) - K N(a_2)\right),

   .. math::

      P_0^G \;=\; e^{-rT}\left(KN(-a_2) - \overline{G}N(-a_1)\right).

   Put--call parity becomes

   .. math::

      C_0^G - P_0^G
      \;=\;
      e^{-rT}\left(\E^{\Q}[G_T] - K\right).

.. admonition:: Monte Carlo estimator
   :class: defbox

   For simulated discounted payoffs :math:`Y^{(1)},\ldots,Y^{(N)}`,

   .. math::

      \widehat{\Price{0}}_N
      \;=\;
      \frac{1}{N}\sum_{i=1}^N Y^{(i)}.

   The statistical error decreases as :math:`N^{-1/2}`. The implementation
   uses ``numpy.random.default_rng(seed)`` so repeated calls with the same seed
   return the same estimator.

.. admonition:: Discrete Asian approximation
   :class: defbox

   For Monte Carlo pricing of the geometric Asian option, the continuous
   average is approximated on a uniform grid
   :math:`0=t_0<t_1<\cdots<t_n=T` by

   .. math::

      G_T^{(n)}
      \;=\;
      \exp\!\left(\frac{1}{n}\sum_{k=1}^{n}\log S_{t_k}\right).

   The engine simulates all paths at once with NumPy arrays and computes this
   average without looping over paths.

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
