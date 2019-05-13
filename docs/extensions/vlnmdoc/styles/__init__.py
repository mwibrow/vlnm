"""
Set up sass.
"""
import os

import sass

from ..mdcolors import MD_PALETTE, mdcolor

WHERE_AM_I = os.path.dirname(__file__)


def setup_sass(css_path, **sass_vars):
    """Setup sass."""
    os.makedirs(os.path.dirname(css_path), exist_ok=True)

    sass_vars = [f'${var.replace("_", "-")}: {val};' for var, val in sass_vars.items()]
    header = '\n'.join(sass_vars) + '\n'
    with open(os.path.join(WHERE_AM_I, 'main.scss'), 'r') as file_in:
        source = file_in.read()
    if source:
        css = sass.compile(
            string=header + source,
            include_paths=[WHERE_AM_I])
    else:
        css = ''
    with open(css_path, 'w') as file_out:
        file_out.write(css)
