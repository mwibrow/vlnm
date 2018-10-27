"""
Plotting extension.
"""
from io import BytesIO, StringIO
import base64
import sys

import docutils.nodes
from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.directives import images
import matplotlib

class PlotDirective(Directive):
    """Class for processing the :rst:dir:`bibliography` directive.
    """
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    has_content = True

    def run(self):
        """Run directive"""
        code = u'\n'.join(self.content)

        matplotlib.use('svg')
        context = dict(plt=None)
        exec(code, context)  # pylint: disable=exec-used
        plt = context['plt']

        output = BytesIO()
        plt.savefig(output, format='png')
        output.seek(0)
        image_data = base64.b64encode(output.getvalue()).decode('ascii')
        image_uri = u'data:image/png;base64,{}'.format(image_data)
        image_node = docutils.nodes.image('', uri=image_uri)
        return [image_node]



def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('plot', PlotDirective)
