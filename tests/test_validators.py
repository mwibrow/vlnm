"""
Tests for the validation module
"""
import unittest

import pandas as pd

from vlnm.decorators import (
    Columns,
    Keywords,
    Returns)
from vlnm.validation import (
    validate_choice_columns,
    validate_choice_keywords,
    validate_columns,
    validate_keywords,
    validate_required_columns,
    validate_required_keywords)