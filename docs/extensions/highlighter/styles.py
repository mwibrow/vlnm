"""
Custom Pygments style.
"""


from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Literal, \
    Number, Other, Operator, Punctuation, Generic, Text, Whitespace

from .colors import mdcolor

YELLOW = mdcolor('amber', 800)
ORANGE = mdcolor('orange', 800)
BLUE = mdcolor('light-blue', 800)
BROWN = mdcolor('brown', 400)
GREEN = mdcolor('light-green', 800)
GREY = mdcolor('blue-grey', 800)
LIGHT_GREY = mdcolor('blue-grey', 400)
PINK = mdcolor('pink', 800)
PURPLE = mdcolor('deep-purple', 800)
RED = mdcolor('red', 400)
YELLOW = mdcolor('amber', 800)


class MaterialStyle(Style):

    background_color = mdcolor('blue-grey', 50)
    highlight_color = mdcolor('blue-grey', 100)

    styles = {
        # No corresponding class for the following:
        Text:                      GREY,  # class:  ''
        Whitespace:                "",        # class: 'w'
        Error:                     RED,  # class: 'err'
        Other:                     "",        # class 'x'

        Comment:                   f"italic {BROWN}",  # class: 'c'
        Comment.Multiline:         "",        # class: 'cm'
        Comment.Preproc:           "",        # class: 'cp'
        Comment.Single:            "",        # class: 'c1'
        Comment.Special:           "",        # class: 'cs'

        Keyword:                   f"bold {GREEN}",  # class: 'k'
        Keyword.Constant:          "",        # class: 'kc'
        Keyword.Declaration:       "",        # class: 'kd'
        Keyword.Namespace:         "",        # class: 'kn'
        Keyword.Pseudo:            "",        # class: 'kp'
        Keyword.Reserved:          "",        # class: 'kr'
        Keyword.Type:              "",        # class: 'kt'

        Operator:                  PINK,  # class: 'o'
        Operator.Word:             "",        # class: 'ow' - like keywords

        Punctuation:               LIGHT_GREY,  # class: 'p'

        Name:                      GREY,  # class: 'n'
        Name.Attribute:            "",  # class: 'na' - to be revised
        Name.Builtin:              GREEN,        # class: 'nb'
        Name.Builtin.Pseudo:       GREEN,        # class: 'bp'
        Name.Class:                f"bold {BLUE}",  # class: 'nc'
        Name.Constant:             "",  # class: 'no' - to be revised
        Name.Decorator:            f"italic {BLUE}",  # class: 'nd'
        Name.Entity:               "",        # class: 'ni'
        Name.Exception:            "",  # class: 'ne'
        Name.Function:             BLUE,  # class: 'nf'
        Name.Function.Magic:       BLUE,  # class: 'nf'
        Name.Property:             "",        # class: 'py'
        Name.Label:                "",        # class: 'nl'
        Name.Namespace:            f"bold {BLUE}",        # class: 'nn' - to be revised
        Name.Other:                "",  # class: 'nx'
        Name.Tag:                  "",  # class: 'nt' - like a keyword
        Name.Variable:             "",        # class: 'nv' - to be revised
        Name.Variable.Class:       "",        # class: 'vc' - to be revised
        Name.Variable.Global:      "",        # class: 'vg' - to be revised
        Name.Variable.Instance:    "",        # class: 'vi' - to be revised

        Number:                    BROWN,  # class: 'm'
        Number.Float:              "",        # class: 'mf'
        Number.Hex:                "",        # class: 'mh'
        Number.Integer:            "",        # class: 'mi'
        Number.Integer.Long:       "",        # class: 'il'
        Number.Oct:                "",        # class: 'mo'

        Literal:                   "",  # class: 'l'
        Literal.Date:              "",  # class: 'ld'

        String:                    BLUE,  # class: 's'
        String.Affix:              PINK,  # class: 'sa'
        String.Backtick:           "",        # class: 'sb'
        String.Char:               "",        # class: 'sc'
        String.Doc:                "italic",        # class: 'sd' - like a comment
        String.Double:             "",        # class: 's2'
        String.Escape:             "",  # class: 'se'
        String.Heredoc:            "",        # class: 'sh'
        String.Interpol:           "",        # class: 'si'
        String.Other:              "",        # class: 'sx'
        String.Regex:              "",        # class: 'sr'
        String.Single:             "",        # class: 's1'
        String.Symbol:             "",        # class: 'ss'

        Generic:                   "",        # class: 'g'
        Generic.Deleted:           "",        # class: 'gd',
        Generic.Emph:              "italic",  # class: 'ge'
        Generic.Error:             "",        # class: 'gr'
        Generic.Heading:           "",        # class: 'gh'
        Generic.Inserted:          "",        # class: 'gi'
        Generic.Output:            "",        # class: 'go'
        Generic.Prompt:            "",        # class: 'gp'
        Generic.Strong:            "bold",    # class: 'gs'
        Generic.Subheading:        "",        # class: 'gu'
        Generic.Traceback:         "",        # class: 'gt'
    }
