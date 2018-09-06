"""
Class decorators for normalizers.
"""

def docstring(cls):
    """
    Decorator for auto generating docstrings
    """
    return cls



def columns(column_spec):
    """
    Decorator for specifying require and optional data frame columns.
    """
    def cls_decorator(cls):
        """
        Decorate {cls} with {column_spec}
        """
        cls._column_spec = column_spec  # pylint: disable=protected-access
    return cls_decorator
