"""
Table extension
"""
from docutils import io, nodes, statemachine, utils
from docutils.parsers.rst.directives.tables import CSVTable
from docutils.parsers.rst import directives

class CSVTabular(CSVTable):
    """Class for typesetting CSV tables with a limited number of rows."""
    option_spec = CSVTable.option_spec
    option_spec['rows'] = directives.nonnegative_int
    option_spec['pre-rows'] = directives.nonnegative_int
    option_spec['post-rows'] = directives.nonnegative_int
    def parse_csv_data_into_rows(self, csv_data, dialect, source):
        """Parse csv file."""
        pre_rows = self.options.get('pre-rows', self.options.get('rows'))
        post_rows = self.options.get('post-rows')
        rows, max_cols = super(CSVTabular, self).parse_csv_data_into_rows(
            csv_data, dialect, source)

        if pre_rows:
            pre = rows[:pre_rows]
            post = rows[-post_rows:] if post_rows else []
            row_data = []
            for _ in range(max_cols):
                cell_data = (0, 0, 0, statemachine.StringList(
                    ['…'], source=source))
                row_data.append(cell_data)
            pre.append(row_data)
            if post:
                pre.extend(post)
            rows = pre
        return rows, max_cols

def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('csv-tabular', CSVTabular)
