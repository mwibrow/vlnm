"""
Tests for the vlnm.plotting.elements module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest
from unittest.mock import (MagicMock, patch)
from vlnm.plotting.elements import (
    bind,
    singleton,
    PlotElement,
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


class TestVowelPlotPlotElement(unittest.TestCase):
    """Tests for the VowelPlotPlotElement."""

    def setUp(self):
        self.patcher = patch('vlnm.plotting.elements.VowelPlot')
        self.mock_vowelplot_class = self.patcher.start()
        self.mock_vowelplot = MagicMock()
        self.mock_vowelplot_class.return_value = self.mock_vowelplot

    def tearDown(self):
        self.patcher.stop()

    def test_begin_end(self):
        """Test begin and end"""
        plot = VowelPlotPlotElement()
        plot.begin()
        plot.end()
        self.mock_vowelplot.legend.assert_called_once()

    def test_context_manager(self):
        """VowelPlot legend called"""
        with VowelPlotPlotElement():
            pass
        self.mock_vowelplot.legend.assert_called_once()

    def test_nested(self):
        """Nested plot raises error"""
        with self.assertRaises(ValueError):
            with VowelPlotPlotElement():
                with VowelPlotPlotElement():
                    pass


class TestMarkersPlotElement(unittest.TestCase):
    """Tests for the MarkersPlotElement class"""

    def setUp(self):
        PlotElement.scp(None)

    def tearDown(self):
        PlotElement.scp(None)

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

    @patch('vlnm.plotting.elements.VowelPlot')
    def test_call(self, mock_vowelplot_class):
        """VowelPlot.markers called"""
        mock_vowelplot = MagicMock()
        mock_vowelplot_class.return_value = mock_vowelplot
        VowelPlotPlotElement().begin()

        markers = MarkersPlotElement()
        markers(color_by='vowel', colors='black')
