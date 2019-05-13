"""
Set up fonts.
"""
from distutils.dir_util import copy_tree
import os

WHERE_AM_I = os.path.abspath(os.path.dirname(__file__))


def setup_fonts(fonts_path):
    """Copy fonts."""
    os.makedirs(fonts_path, exist_ok=True)
    copy_tree(os.path.join(WHERE_AM_I, 'fonts'), fonts_path)
