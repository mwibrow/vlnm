"""
Class decorators for normalizers.
"""
import re

def docstring(cls):
    """
    Decorator for auto generating docstrings
    """
    try:
        column_specs = getattr(cls, '_column_specs')
        cls.__doc__ = re.sub('{% columns %}', column_specs_docstring(column_specs), cls.__doc__)
    except AttributeError:
        pass

    return cls

def column_specs_docstring(column_spec):
    """Generate documentation from the column spec. for a class.
    """
    return 'Nope'



def columns(**column_specs):
    """
    Decorator for specifying require and optional data frame columns.
    """
    def cls_decorator(cls):
        """
        Decorate {cls} with {column_specs}
        """
        cls._column_specs = column_specs  # pylint: disable=protected-access
        return cls
    return cls_decorator
