# Derivatives Pricing

Python library implementing classical derivatives pricing methods with a
modular architecture. The project covers lattice methods, Black-Scholes
pricing, Monte Carlo simulation, Greeks, cost-of-carry variants, static
arbitrage checks and finite-difference PDE solvers.

The package is intentionally compact: the public surface is concentrated in
`derivatives_pricing.api`, while internal modules separate contracts, market
data, models, engines and pricers.

## Features

- European option pricing with a binomial tree.
- Black-Scholes analytical pricing for European options.
- Monte Carlo pricing for European and geometric Asian options.
- Analytical and finite-difference Greeks.
- Continuous dividend yield, FX options and futures options through
  cost-of-carry.
- Static arbitrage diagnostics on discrete call price surfaces.
- Explicit and implicit finite-difference solvers for the heat equation.
- Black-Scholes pricing through the heat-equation transformation.

## Installation

The project targets Python 3.13.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Runtime dependencies are declared in `pyproject.toml`: NumPy and SciPy.

## Quick Example

```python
import derivatives_pricing.api as pricing

price = pricing.get_price_bs_european(
    St=100.0,
    K=100.0,
    T=1.0,
    r=0.03,
    sigma=0.20,
    call=True,
)

delta = pricing.get_greek_bs_european(
    St=100.0,
    K=100.0,
    T=1.0,
    r=0.03,
    sigma=0.20,
    call=True,
    greek="delta",
)

print(price, delta)
```

## Project Structure

```text
derivatives_pricing/
  api.py                 # stable public facade
  contracts/             # option contracts and payoff-like adapters
  market/                # market data, curves and call surfaces
  models/                # binomial, Black-Scholes and PDE models
  engines/               # analytical, tree, Monte Carlo and PDE engines
  greeks/                # analytical and finite-difference Greeks
  pricers/               # contract + market + model + engine orchestration
  utils/                 # shared numerical helpers
tests/                   # pytest regression tests
docs/                    # Sphinx documentation
```

## Development Commands

```bash
pytest tests
python -m build --wheel
python -m sphinx -b html docs/source docs/build/html
```

## Design Notes

The library keeps pricing concerns separate:

- **Contracts** describe payoff structure.
- **Market** objects provide spots, curves and observed surfaces.
- **Models** parameterize stochastic or PDE dynamics.
- **Engines** implement numerical algorithms.
- **Pricers** combine the previous layers.

The facade in `derivatives_pricing.api` provides simple functions for common
pricing tasks while leaving the internal architecture extensible.

## Disclaimer

This project is for educational and research purposes. It is not financial
advice and should not be used as the sole basis for trading, risk management or
investment decisions.
