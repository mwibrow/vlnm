"""
Plotting extension.
"""
from io import BytesIO, StringIO
import base64
import sys

import docutils.nodes
from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.directives import images


class PlotDirective(Directive):
    """Class for processing the :rst:dir:`bibliography` directive.
    """
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    has_content = True

    option_spec = {
        'backend': directives.unchanged,
        'figure': directives.unchanged,
        'imports': directives.unchanged
    }

    def run(self):
        """Run directive"""
        statements = u'\n'.join([
            line for line in self.content if not line.startswith('###')])
        code = u'\n'.join(line[4:] if line.startswith('###') else line
                          for line in self.content)
        imports = self.options.get('imports', '')
        backend = self.options.get('backend', 'agg')
        code = '{}\nimport matplotlib\nmatplotlib.use("{}")\n{}'.format(
            imports, backend, code)
        if self.options.get('figure'):
            code = '{}\n__figure__ = {}'.format(code, self.options['figure'])
        env = {}
        exec(code, env)  # pylint: disable=exec-used
        figure = env.get('__figure__')

        output = BytesIO()
        figure.savefig(output, format='png', bbox_inches='tight')
        output.seek(0)
        image_data = base64.b64encode(output.getvalue()).decode('ascii')
        image_uri = u'data:image/png;base64,{}'.format(image_data)
        image_node = docutils.nodes.image('', uri=image_uri)

        parent = docutils.nodes.paragraph()
        code = docutils.nodes.literal_block(statements, statements)
        code['language'] = 'python'
        parent += code
        parent += image_node
        return [parent]



def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('plot', PlotDirective)
