# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import importlib.metadata
import os
import sys

sys.path.append(os.path.abspath("_ext"))
release = importlib.metadata.version("ewokssoleildemo")

project = "ewokssoleildemo"
version = ".".join(release.split(".")[:2])
copyright = "2026, ESRF"
author = "ESRF"
docstitle = f"{project} {version}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "ewokssphinx",
    "make_pymca_config",
]
templates_path = ["_templates"]
exclude_patterns = []

always_document_param_types = True

autosummary_generate = True

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_title = docstitle
# html_logo = "_static/logo.png"
html_static_path = ["_static"]
html_template_path = ["_templates"]
html_css_files = ["custom.css"]

html_theme_options = {
    "icon_links": [
        {
            "name": "github",
            "url": "https://github.com/ewoks-apps/ewokssoleildemo",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "pypi",
            "url": "https://pypi.org/project/ewokssoleildemo",
            "icon": "fa-brands fa-python",
        },
    ],
    "logo": {
        "text": docstitle,
    },
    "footer_start": ["copyright"],
    "footer_end": ["footer_end"],
}
