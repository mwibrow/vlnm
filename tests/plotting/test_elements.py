"""
Tests for the vlnm.plotting.elements module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest
from unittest.mock import patch
from vlnm.plotting.elements import (
    bind,
    singleton,
    MarkersPlotElement,
    VowelPlotPlotElement,
)


class TestSingleton(unittest.TestCase):
    """Tests for the singleton decorator."""

    def test_singleton(self):
        """Objects have same id"""

        @singleton
        class Test:
            pass

        obj1 = Test()
        obj2 = Test()
        self.assertEqual(id(obj1), id(obj2))


class TestBind(unittest.TestCase):
    """Tests for the bind decorator"""

    def test_bind(self):
        """Correctly bind to method"""

        class Bindable:
            def to_bind(self):  # pylint: disable=no-self-use
                return 'value'

        @bind(Bindable.to_bind)
        class Klass:
            def __call__(self):
                pass

        obj = Klass()
        value = obj()
        self.assertEqual(value, 'value')

    def test_bind_with_parent(self):
        """Call parent before bound method."""

        class Bindable:
            def to_bind(self):  # pylint: disable=no-self-use
                return 'value'

        class Parent:
            called = False

            def __call__(self, *args, **kwargs):
                Parent.called = True

        @bind(Bindable.to_bind)
        class Child(Parent):
            pass

        obj = Child()
        value = obj()
        self.assertEqual(value, 'value')
        self.assertTrue(Parent.called)


class TestMarkersPlotElement(unittest.TestCase):
    """Tests for the MarkersPlotElement class"""

    def test_is_singleton(self):
        """Class is singleton"""
        objId = id(MarkersPlotElement())
        self.assertTrue(all(
            id(MarkersPlotElement()) == objId
            for _ in range(10)))

    def test_no_vowel_plot(self):
        """No vowel plot raises error"""
        with self.assertRaises(ValueError):
            markers = MarkersPlotElement()
            markers()

    # @patch('vlnm.plotting.VowelPlot')
    # def test_call(self, mockMarkers):
    #     """VowelPlot.markers called"""

    #     with VowelPlotPlotElement().begin():
    #         markers = MarkersPlotElement()
    #         markers(color_by='vowel', colors='black')
    #         mockMarkers.assert_called_once()
