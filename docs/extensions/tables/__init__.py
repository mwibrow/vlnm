"""
Table extension
"""
from docutils import io, nodes, statemachine, utils
from docutils.parsers.rst.directives.tables import CSVTable
from docutils.parsers.rst import directives

class CSVTabular(CSVTable):
    """Class for typesetting CSV tables with a limited number of rows."""
    option_spec = CSVTable.option_spec
    option_spec['rows'] = directives.unchanged
    option_spec['truncate'] = directives.nonnegative_int
    option_spec['index'] = directives.flag

    def parse_csv_data_into_rows(self, csv_data, dialect, source):
        """Parse csv file."""
        row_specs = self.options.get('rows')
        truncate = self.options.get('truncate')
        rows, max_cols = super(
            CSVTabular, self).parse_csv_data_into_rows(
                csv_data, dialect, source)
        if 'index' in self.options:
            max_cols += 1
            rows[0].insert(0, (0, 0, 0, statemachine.StringList(
                ['row'], source=source)))
            for i in range(1, len(rows)):
                rows[i].insert(0, (0, 0, 0, statemachine.StringList(
                    [str(i)], source=source)))
        header = self.options.get('header-rows', 0)

        if row_specs:
            new_rows = []
            if header:
                new_rows.extend(rows[:header])
            for i, row_spec in enumerate(row_specs.split(',')):
                start, end = parse_row_spec(row_spec)
                start = start or header
                end = end + header if end else len(rows)
                new_rows.extend(rows[slice(start, end)])
                if i < len(row_specs) and end and end < len(rows):
                    row_data = []
                    for _ in range(max_cols):
                        cell_data = (0, 0, 0, statemachine.StringList(
                            ['⋮'], source=source))
                        row_data.append(cell_data)
                    new_rows.append(row_data)
            rows = new_rows

        if truncate:
            for row in rows:
                for col in row:
                    col[3][0] = col[3][0][:truncate]
        return rows, max_cols

def parse_row_spec(spec):
    """Parse a row spec """
    indices = [int(number) if number else None
               for number in spec.split('..')]
    if len(indices) == 1:
        return indices[0], indices[1] + 1
    return indices[:2]
def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('csv-tabular', CSVTabular)
