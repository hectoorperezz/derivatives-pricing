# Derivatives Pricing Library Hesperides

Python library for pricing financial derivatives. Course project for *Asset Pricing Fundamentals* and *Interest Rate Models*.

**We use Python 3.13.** Declare `requires-python = "==3.13.*"` in `pyproject.toml`.

## Goal
You will build your own pricing library incrementally, adding new derivatives and models in each assignment, following good software engineering practices.

## Requirements
- Clean, modular architecture.
- Deliver a **wheel** (`.whl`) for each assignment and ensure all tests pass.
- Public tests are included in the repo and must pass before submission.
- Private tests are used by us for grading.
- Submissions are cumulative: each one must include all previous functionality.
- Keep `pyproject.toml` in the repo.

---

## Modular Architecture

Build a **modular, maintainable, and extensible** library for derivatives pricing, with clear separation among the following parts.

- **Contracts / Instruments** (what is being priced).
- **Market** (curves, forwards, volatilities, fixings).
- **Models** (dynamics under the pricing measure).
- **Engines** (algorithms: analytical, tree, MC, PDE).
- **Pricers** (orchestration: combines contract + market + model + engine).

---

## Submission Requirements
- Clean and modular architecture (see package structure).
- **Single public interface** for tests: `hesperides/api.py`.
- Public tests are included in the repo.
- Private tests are used by us for grading.
- Submission in **wheel** format (`.whl`) and **all tests must pass**.

---

## Testing and Wheel

A wheel is a built, installable Python package file (`.whl`) that contains your code and metadata, so it can be installed quickly without recompiling or copying sources. In this course, we install your wheel in a clean environment and run the tests against that installed package.

### How to create a wheel
1. Make sure dependencies are declared in `pyproject.toml`.
2. Install build tooling (once).
   ```bash
   python -m pip install -U build
   ```
3. Build the wheel from the project root.
   ```bash
   python -m build --wheel
   ```
4. The wheel will be in `dist/` (e.g., `dist/hesperides-0.?.?-py3-none-any.whl`).



### 1) Single Public Interface: `hesperides.api`
Tests (both public and private) can **ONLY** do the following.

```python
import hesperides.api as hapi
```

Therefore, follow these rules.

- `hesperides/api.py` is the **only public interface**.
- The rest of the package is **internal** and can change as long as the API is not broken.

### 2) Private Tests Philosophy
Private tests typically do the following.

1. Generate inputs (test cases).
2. Call **facade functions** from `hesperides.api` with an **exact signature**.
3. Check expected values / properties (bounds, monotonicity, put-call parity…) / references.

If the assignment asks for a function `get_price_binomial_european_call(...)`, that function must exist in `api.py` and behave as specified.

In any case, you can also check your code with your own tests, taking examples from the list of exercises in the course or other sources, like Privault's exercises.

---

## API Contract (`hesperides/api.py`)

### Principles
- `api.py` exposes **simple and stable facade functions**.
- Inputs and outputs as specified in each assignment.


**(A) Assignment-specific functions (mandatory if requested)**  
Example: binomial for European call. 

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
    ...
```


---

## Performance

> **Using loops instead of vectorized NumPy code will be penalized.**

Specific requirements will be defined in each assignment. An example of an unacceptable loop would be iterating over Monte Carlo paths during simulation when NumPy vectorization (using array operations and broadcasting instead of Python loops) is expected; see the NumPy broadcasting guide: https://numpy.org/doc/stable/user/basics.broadcasting.html.

Also follow the best practices explained in *Fundamentos de Python* for NumPy course: specify `dtype` when possible for additional optimization, use views instead of copies when a copy is not needed, and apply vectorization patterns where appropriate.

> **Monte Carlo must be reproducible through seeds.**

This will be detailed in the corresponding assignments.



---


## Packaging and Submission

### Submission
- Submit an installable `.whl`.
  ```bash
  pip install dist/hesperides-0.?.?-py3-none-any.whl
  ```

### Checklist Before Submitting
1. Install in a clean environment.
   ```bash
   pip install dist/*.whl
   ```
2. Basic import.
   ```bash
   python -c "import hesperides; import hesperides.api as hapi"
   ```
3. Run public tests.
   ```bash
   pytest
   ```

Note that test files must follow pytest's naming conventions to be discovered. Check the [pytest documentation](https://docs.pytest.org/en/stable/getting-started.html#directory-structure) for more details.

---

## Dependencies and Grading Environment

For grading, we will install your wheel in a **clean environment** (a freshly created virtual environment) and run the tests. In that environment, **only the dependencies declared** by your package (and those allowed by the course) will be available.

### Key Rules

1. **If you import a library that is not declared as a runtime dependency in `pyproject.toml`**, the installation/execution will fail (`ModuleNotFoundError`).

2. **Clearly separate runtime dependencies from development dependencies.**
   - **Runtime** (in `[project].dependencies`): required to use the library (such as `numpy`).
   - **Development** (in `[project.optional-dependencies].dev`): only for testing/linting (such as `pytest`).

3. **Avoid unnecessary dependencies:** grading assumes a minimal and reproducible environment. Use only standard/approved libraries unless explicitly permitted.

### Example `pyproject.toml`

```toml
# Build system: how the package is built (PEP 517)
[build-system]
requires = ["setuptools>=69", "wheel"]  # Build-time dependencies. Needed to create the wheel.
build-backend = "setuptools.build_meta"  # Entry point for building

# Project metadata and install requirements
[project]
name = "pricing_hesperides"
version = "0.1.0"
description = "Library for asset pricing"
readme = "README.md"
requires-python = "==3.13.*"
dependencies = ["numpy>=2.0.0"]  # Runtime dependencies. Needed to run use the library after install.

# Optional dependency groups (pip install .[dev])
[project.optional-dependencies]
dev = ["pytest>=8.2", "pytest-timeout>=2.2", "build>=1.2", "ruff>=0.6", "mypy>=1.10"]

```

---

## Validate the full process from scratch in a clean environment.

From the project root, run the following in order: 
- Create a venv and activate it.
- Upgrade pip and install build.
- Build the wheel.
- Install the wheel and dev dependencies (pytest, etc.).
- Run tests.

   ```bash
   py -3.13 -m venv .venv-wheel
   .venv-wheel\Scripts\activate
   python -m pip install -U pip build
   python -m build --wheel
   python -m pip install dist/pricing_hesperides-0.1.0-py3-none-any.whl
   python -m pip install .[dev]
   python -m pytest
   ```
### Grading Process

In practice, grading will use an isolated environment and your built wheel from `dist/` is installed (and nothing else from the repo). Then the test suite is run with pytest. Your submission must pass these tests with only the dependencies declared in `pyproject.toml`; no extra packages or local source imports are available.

For instance, if your code does `import pandas` but `pandas` is not in `dependencies`, the test will fail with `ModuleNotFoundError: No module named 'pandas'`. This will result in a failed submission.

