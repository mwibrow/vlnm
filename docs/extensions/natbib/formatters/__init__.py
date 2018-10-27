"""
Formatters
"""

from .authoryear import AuthorYearFormatter

def get_formatter(style):
    """Get the formatter class."""
    if style == 'authoryear':
        return AuthorYearFormatter
    return AuthorYearFormatter
