"""Sphinx configuration for the Derivatives Pricing library."""

from __future__ import annotations

import sys
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version as pkg_version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# -- Project information -----------------------------------------------------
project = "Derivatives Pricing"
author = "Héctor Pérez Ledesma"
copyright = f"{datetime.now():%Y}, {author}"

try:
    release = pkg_version("derivatives-pricing")
except PackageNotFoundError:
    release = "0.0.0"
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_design",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = []

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

language = "en"

# -- Autodoc / Autosummary ---------------------------------------------------
autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
autodoc_typehints_format = "short"
typehints_fully_qualified = False
always_document_param_types = True

# -- Napoleon ----------------------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_use_rtype = False
napoleon_use_param = True

# -- Intersphinx -------------------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

# -- MyST --------------------------------------------------------------------
myst_enable_extensions = [
    "deflist",
    "colon_fence",
    "dollarmath",
    "amsmath",
]
myst_heading_anchors = 3

# -- HTML output -------------------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
html_css_files = [
    "https://rsms.me/inter/inter.css",
    "https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@v2.304/css/jetbrains-mono.css",
    "derivatives_pricing.css",
]
html_title = "Derivatives Pricing"
html_short_title = "Derivatives Pricing"
html_show_sphinx = False
html_show_copyright = True
pygments_style = "default"
pygments_dark_style = "github-dark"

# Derivatives Pricing palette ------------------------------------------------
ACCENT_GOLD = "#FFCD00"
ACCENT_GOLD_HOVER = "#FFD940"
ACCENT_GOLD_DEEP = "#B38F00"

html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_buttons": ["view"],
    "light_css_variables": {
        "color-brand-primary": ACCENT_GOLD,
        "color-brand-content": ACCENT_GOLD,
        "color-brand-visited": ACCENT_GOLD,
        # surfaces
        "color-background-primary": "#ffffff",
        "color-background-secondary": "#fafafa",
        "color-background-hover": "#f5f5f5",
        "color-background-border": "rgba(0, 0, 0, 0.08)",
        "color-foreground-primary": "#0a0a0a",
        "color-foreground-secondary": "#525252",
        "color-foreground-muted": "#737373",
        "color-foreground-border": "rgba(0, 0, 0, 0.12)",
        # code
        "color-inline-code-background": "#f4f4f5",
        "color-highlighted-background": "#fff4cc",
        # fonts
        "font-stack": (
            "'Inter var', Inter, -apple-system, BlinkMacSystemFont, "
            "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
        ),
        "font-stack--monospace": (
            "'JetBrains Mono', 'SF Mono', ui-monospace, Menlo, Monaco, "
            "Consolas, 'Liberation Mono', monospace"
        ),
        # admonitions
        "color-admonition-background": "#fafafa",
        # api
        "color-api-name": ACCENT_GOLD,
        "color-api-pre-name": ACCENT_GOLD,
        # sidebar
        "color-sidebar-link-text--top-level": "#0a0a0a",
        "color-sidebar-background": "#fafafa",
        "color-sidebar-background-border": "rgba(0, 0, 0, 0.06)",
        # spacing
        "sidebar-width": "17rem",
        "page-width": "78rem",
        "content-padding": "3rem",
        "header-height": "3.5rem",
    },
    "dark_css_variables": {
        "color-brand-primary": ACCENT_GOLD,
        "color-brand-content": ACCENT_GOLD,
        "color-brand-visited": ACCENT_GOLD,
        "color-background-primary": "#0a0a0a",
        "color-background-secondary": "#111111",
        "color-background-hover": "#1a1a1a",
        "color-background-border": "rgba(255, 255, 255, 0.08)",
        "color-foreground-primary": "#ededed",
        "color-foreground-secondary": "#a3a3a3",
        "color-foreground-muted": "#737373",
        "color-foreground-border": "rgba(255, 255, 255, 0.12)",
        "color-inline-code-background": "#1a1a1a",
        "color-highlighted-background": "rgba(245, 180, 0, 0.18)",
        "color-admonition-background": "#111111",
        "color-api-name": ACCENT_GOLD,
        "color-api-pre-name": ACCENT_GOLD,
        "color-sidebar-link-text--top-level": "#ededed",
        "color-sidebar-background": "#0a0a0a",
        "color-sidebar-background-border": "rgba(255, 255, 255, 0.06)",
    },
}

# -- MathJax 3 ---------------------------------------------------------------
mathjax_path = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"
mathjax3_config = {
    "tex": {
        "inlineMath": [["$", "$"], ["\\(", "\\)"]],
        "displayMath": [["$$", "$$"], ["\\[", "\\]"]],
        "processEscapes": True,
        "tags": "ams",
        "macros": {
            # Sets and measures
            "R": r"\mathbb{R}",
            "E": r"\mathbb{E}",
            "P": r"\mathbb{P}",
            "Q": r"\mathbb{Q}",
            "Filt": r"\mathcal{F}",
            "Sigma": r"\mathcal{G}",
            "Omega": r"\Omega",
            # Operadores
            "Var": r"\operatorname{Var}",
            "Cov": r"\operatorname{Cov}",
            "Corr": r"\operatorname{Corr}",
            "ind": [r"\mathbf{1}_{#1}", 1],
            "argmax": r"\operatorname*{arg\,max}",
            "argmin": r"\operatorname*{arg\,min}",
            # Tiempo y diferenciales
            "dd": r"\mathrm{d}",
            "dt": r"\,\mathrm{d}t",
            "dW": r"\,\mathrm{d}W",
            "dS": r"\,\mathrm{d}S",
            # Pricing
            "Price": [r"\Pi_{#1}", 1],
            "payoff": r"\Phi",
            "num": r"\mathrm{num}",
            # Otros
            "normal": [r"\mathcal{N}\!\left(#1,\,#2\right)", 2],
            "abs": [r"\left\lvert #1 \right\rvert", 1],
            "norm": [r"\left\lVert #1 \right\rVert", 1],
            "pos": [r"\left(#1\right)^{+}", 1],
            "iidsim": r"\stackrel{\mathrm{i.i.d.}}{\sim}",
            "indep": r"\perp\!\!\!\perp",
        },
    },
    "chtml": {
        "scale": 0.95,
        "displayAlign": "center",
        "displayIndent": "0",
    },
}
# Let myst-parser augment processHtmlClass with its own marker classes.
suppress_warnings = ["myst.mathjax"]

# -- Misc --------------------------------------------------------------------
nitpicky = False
add_module_names = False
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
