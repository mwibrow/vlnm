"""
Extension providing custom lexers.
"""
import os
import setuptools

ENTRY_POINTS = """
[pygments.lexers]
py3ext = extensions.highlighter.lexers:Python3LexerExtended
[pygments.styles]
material = extensions.highlighter.styles:MaterialStyle
"""


class CleanCommand(setuptools.Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):  # pylint: disable = no-self-use
        os.system('rm -vrf ./dist ./highlighter.egg-info')


def setup(_app):
    setuptools.setup(
        script_name='setup.py',
        script_args=['install', 'clean', '--all', 'deepclean'],
        name='highlighter',
        version='0.1',
        description=__doc__,
        author='Mark Wibrow',
        packages=['extensions.highlighter'],
        entry_points=ENTRY_POINTS,
        cmdclass={
            'deepclean': CleanCommand,
        })
