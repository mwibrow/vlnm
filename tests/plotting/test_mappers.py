"""
Tests for the vlnm.plotting.mappers module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest

from vlnm.plotting.mappers import PropMapper


class TestPropMapper(unittest.TestCase):
    """Tests for the PropMapper class."""

    def test_init_no_args(self):
        """Create instance without error."""
        mapper = PropMapper()

    def test_dict_mapper_value(self):
        """Dict mapping returns correct props value."""
        mapper = PropMapper(prop='prop', mapping=dict(a=1))
        props = mapper.get_props('a')
        self.assertDictEqual(props, dict(prop=1))

    def test_dict_mapper_dict(self):
        """Dict mapping returns correct props dict."""
        mapper = PropMapper(mapping=dict(a=dict(b=2)))
        props = mapper.get_props('a')
        self.assertDictEqual(props, dict(b=2))

    def test_dict_mapper_default_value(self):
        """Dict mapping returns correct default props value."""
        mapper = PropMapper(prop='prop', mapping=dict(a=1), default=2)
        props = mapper.get_props('b')
        self.assertDictEqual(props, dict(prop=2))

    def test_dict_mapper_default_dict(self):
        """Dict mapping returns correct default props dict."""
        mapper = PropMapper(mapping=dict(a=1), default=dict(prop=2))
        props = mapper.get_props('b')
        self.assertDictEqual(props, dict(prop=2))

    def test_function_mapper_value(self):
        """Function mapping returns correct props value."""
        def mapping(value):
            if value == 'a':
                return 1
            return 2
        mapper = PropMapper(prop='prop', mapping=mapping)
        props = mapper.get_props('a')
        self.assertDictEqual(props, dict(prop=1))

    def test_function_mapper_dict(self):
        """Function mapping returns correct props dict."""
        def mapping(value):
            if value == 'a':
                return dict(prop=1)
            return dict(prop=2)
        mapper = PropMapper(mapping=mapping)
        props = mapper.get_props('a')
        self.assertDictEqual(props, dict(prop=1))
