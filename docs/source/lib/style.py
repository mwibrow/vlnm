"""
Custom Pygments style.
"""


from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Punctuation, Generic, Whitespace

from docs.source.lib.material import mdcolor

class MaterialStyle(Style):

    background_color = "#272822"
    highlight_color = "#49483e"
    styles = {
        # Comment:                f"italic {mdcolor('blue-grey', 300)}",
        # Error: f"italic {mdcolor('red')}",
        # Generic:                mdcolor('blue-grey', 900),
        # Keyword:                f"bold {mdcolor('light-blue', 900)}",
        # Operator: mdcolor('red', 900),
        # Punctuation: mdcolor('red', 900),
        # Name:                   mdcolor('blue-grey', 900),
        # Name.Function:          '#0f0',
        # Name.Variable.Instance: '#0ff',
        # Name.Class:             mdcolor('amber'),
        # Number:                 mdcolor('orange'),
        # String:                 mdcolor('light-green', 900)
        Whitespace:                "#bbbbbb",

        Comment:                   f"italic {mdcolor('blue-grey')}",
        Comment.Preproc:           f"italic {mdcolor('blue-grey')}",
        Comment.Special:           f"bold italic {mdcolor('blue-grey')}",

        Keyword:                   f"bold {mdcolor('light-green', 900)}",
        Keyword.Pseudo:            "#038",
        Keyword.Type:              "#339",

        Operator:                  mdcolor('brown', 500),
        Operator.Word:             mdcolor('brown', 500),

        Punctuation:               mdcolor('brown', 500),

        Name.Builtin:              "#007020",
        Name.Function:             "bold #06B",
        Name.Class:                f"bold {mdcolor('amber', 900)}",
        Name.Namespace:            "bold #0e84b5",
        Name.Exception:            "bold #F00",
        Name.Variable:             "#963",
        Name.Variable.Instance:    "#33B",
        Name.Variable.Class:       "#369",
        Name.Variable.Global:      "bold #d70",
        Name.Constant:             "bold #036",
        Name.Label:                "bold #970",
        Name.Entity:               "bold #800",
        Name.Attribute:            "#00C",
        Name.Tag:                  "#070",
        Name.Decorator:            f"italic {mdcolor('light-blue')}",

        String:                    mdcolor('light-blue', 900),
        String.Char:               mdcolor('light-blue', 900),
        String.Doc:                mdcolor('light-blue', 900),
        String.Interpol:           mdcolor('amber', 900),
        String.Escape:             mdcolor('amber', 900),
        String.Regex:              mdcolor('light-blue'),
        String.Symbol:             mdcolor('light-blue', 900),
        String.Other:              mdcolor('light-blue', 900),

        Number:                    mdcolor('amber', 900),
        Number.Integer:            mdcolor('amber', 900),
        Number.Float:              mdcolor('amber', 900),
        Number.Hex:                mdcolor('amber', 900),
        Number.Oct:                mdcolor('amber', 900),

        Generic.Heading:           "bold #000080",
        Generic.Subheading:        "bold #800080",
        Generic.Deleted:           "#A00000",
        Generic.Inserted:          "#00A000",
        Generic.Error:             "#FF0000",
        Generic.Emph:              "italic",
        Generic.Strong:            "bold",
        Generic.Prompt:            "bold #c65d09",
        Generic.Output:            "#888",
        Generic.Traceback:         "#04D",

        Error: "#F00 bg:#FAA"
    }
