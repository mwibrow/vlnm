"""
Console directive.
"""

from code import InteractiveConsole
from io import StringIO
from contextlib import redirect_stdout


import docutils.nodes
from docutils.parsers.rst import directives, Directive
from sphinx.directives import CodeBlock

class ConsoleDirective(CodeBlock):
    """Class for processing the :rst:dir:`bibliography` directive.
    """

    def run(self):
        """Run directive"""

        statements = []
        console = InteractiveConsole()
        session = StringIO()
        hidden = False
        content = [line for line in self.content]
        for line in content:
            line = line or '\n'
            if line == '###':
                hidden = not hidden
            if line.strip() and not hidden and line != '###':
                statements.append(line)
            output = StringIO()
            with redirect_stdout(output):
                more = console.push(line)
            value = output.getvalue()
            output.close()
            if more:
                continue
            else:
                for i, statement in enumerate(statements):
                    prefix = '...' if i else '>>>'
                    session.write('{} {}\n'.format(prefix, statement))
                session.write(value)
                statements = []

        self.content = session.getvalue().strip().split('\n')
        session.close()
        return super(ConsoleDirective, self).run()

def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('console', ConsoleDirective)
