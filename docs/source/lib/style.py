"""
Custom Pygments style.
"""


from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Literal, \
     Number, Other, Operator, Punctuation, Generic, Text, Whitespace

from docs.source.lib.material import mdcolor

class MaterialStyle(Style):

    background_color = mdcolor('blue-grey', 50)
    highlight_color = mdcolor('blue-grey', 100)

    styles = {
        # No corresponding class for the following:
        Text:                      mdcolor('blue-grey', 900), # class:  ''
        Whitespace:                "",        # class: 'w'
        Error:                     mdcolor('red'), # class: 'err'
        Other:                     "",        # class 'x'

        Comment:                   f"italic {mdcolor('blue-grey', 400)}", # class: 'c'
        Comment.Multiline:         "",        # class: 'cm'
        Comment.Preproc:           "",        # class: 'cp'
        Comment.Single:            "",        # class: 'c1'
        Comment.Special:           "",        # class: 'cs'

        Keyword:                   mdcolor('deep-purple', 800), # class: 'k'
        Keyword.Constant:          "",        # class: 'kc'
        Keyword.Declaration:       "",        # class: 'kd'
        Keyword.Namespace:         "",        # class: 'kn'
        Keyword.Pseudo:            "",        # class: 'kp'
        Keyword.Reserved:          "",        # class: 'kr'
        Keyword.Type:              "",        # class: 'kt'

        Operator:                  mdcolor('pink', 900), # class: 'o'
        Operator.Word:             "",        # class: 'ow' - like keywords

        Punctuation:               mdcolor('blue-grey', 500), # class: 'p'

        Name:                      mdcolor('blue-grey', 800), # class: 'n'
        Name.Attribute:            "", # class: 'na' - to be revised
        Name.Builtin:              "",        # class: 'nb'
        Name.Builtin.Pseudo:       mdcolor('red', 900),        # class: 'bp'
        Name.Class:                f"bold {mdcolor('light-blue', 800)}", # class: 'nc'
        Name.Constant:             mdcolor('red', 900), # class: 'no' - to be revised
        Name.Decorator:            f"italic {mdcolor('light-blue', 800)}", # class: 'nd'
        Name.Entity:               "",        # class: 'ni'
        Name.Exception:            "", # class: 'ne'
        Name.Function:             mdcolor('light-blue', 800), # class: 'nf'
        Name.Function.Magic:       mdcolor('light-blue', 500), # class: 'nf'
        Name.Property:             "",        # class: 'py'
        Name.Label:                "",        # class: 'nl'
        Name.Namespace:            "",        # class: 'nn' - to be revised
        Name.Other:                "", # class: 'nx'
        Name.Tag:                  "", # class: 'nt' - like a keyword
        Name.Variable:             "",        # class: 'nv' - to be revised
        Name.Variable.Class:       "",        # class: 'vc' - to be revised
        Name.Variable.Global:      "",        # class: 'vg' - to be revised
        Name.Variable.Instance:    "",        # class: 'vi' - to be revised

        Number:                    mdcolor('brown', 500), # class: 'm'
        Number.Float:              "",        # class: 'mf'
        Number.Hex:                "",        # class: 'mh'
        Number.Integer:            "",        # class: 'mi'
        Number.Integer.Long:       "",        # class: 'il'
        Number.Oct:                "",        # class: 'mo'

        Literal:                   "", # class: 'l'
        Literal.Date:              "", # class: 'ld'

        String:                    mdcolor('light-green', 800), # class: 's'
        String.Affix:              mdcolor('purple', 800), # class: 'sa'
        String.Backtick:           "",        # class: 'sb'
        String.Char:               "",        # class: 'sc'
        String.Doc:                "italic",        # class: 'sd' - like a comment
        String.Double:             "",        # class: 's2'
        String.Escape:             mdcolor('light-green', 600), # class: 'se'
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
