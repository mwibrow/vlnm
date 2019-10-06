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
    ContoursPlotElement,
    DataPlotElement,
    PolygonsPlotElement,
    LegendPlotElement,
    MarkersPlotElement,
    LabelsPlotElement,
    EllipsesPlotElement,
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

    def test_bind_function(self):
        """Correctly bind to function"""

        def to_bind():
            return 'value'

        @bind(to_bind)
        class Klass:
            def __call__(self):
                pass

        obj = Klass()
        value = obj()
        self.assertEqual(value, 'value')

    def test_bind_method(self):
        """Correctly bind to method"""

        class Bindable:
            def to_bind(self):  # pylint: disable=no-self-use
                return 'value'

        def get_instance():
            return Bindable()

        @bind(Bindable.to_bind, get_instance)
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

        def get_instance():
            return Bindable()

        @bind(Bindable.to_bind, get_instance)
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

    def test_call(self):
        """Test begin with __call__"""
        plot = VowelPlotPlotElement()
        plot()
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


class Helpers:

    class TestPlotElementChildren(unittest.TestCase):

        klass = PlotElement
        method = 'method'

        def setUp(self):
            PlotElement.set_plot(None)
            self.mock_vowelplot = MagicMock()

        def tearDown(self):
            PlotElement.set_plot(None)

        def test_is_singleton(self):
            """Class is singleton"""
            objId = id(self.klass())
            self.assertTrue(all(
                id(self.klass()) == objId
                for _ in range(10)))

        def test_no_vowel_plot(self):
            """No vowel plot raises error"""
            with self.assertRaises(ValueError):
                self.klass()()

        @patch('vlnm.plotting.elements.VowelPlot')
        def test_call(self, mock_vowelplot_class):
            """VowelPlot method called"""
            mock_vowelplot_class.return_value = self.mock_vowelplot
            setattr(self.mock_vowelplot, self.method, MagicMock())
            kwargs = dict(color_by='vowel', colors='black')
            VowelPlotPlotElement().begin()
            self.klass()(**kwargs)
            getattr(self.mock_vowelplot, self.method).assert_called_with(**kwargs)


class TestContoursPlotElement(Helpers.TestPlotElementChildren):
    klass = ContoursPlotElement
    method = 'contours'


class TestEllipsesPlotElement(Helpers.TestPlotElementChildren):
    klass = EllipsesPlotElement
    method = 'ellipses'


class TestLabelsPlotElement(Helpers.TestPlotElementChildren):
    klass = LabelsPlotElement
    method = 'labels'


class TestMarkersPlotElement(Helpers.TestPlotElementChildren):
    klass = MarkersPlotElement
    method = 'markers'


class TestPolygonsPlotElement(Helpers.TestPlotElementChildren):
    klass = PolygonsPlotElement
    method = 'polygons'


class TestLegendPlotElement(Helpers.TestPlotElementChildren):
    klass = LegendPlotElement
    method = 'legend'


class TestDataPlotElement(Helpers.TestPlotElementChildren):
    klass = DataPlotElement
    method = 'data'

    @patch('vlnm.plotting.elements.VowelPlot')
    def test_context(self, mock_vowelplot_class):
        """Data context pops settings."""
        mock_vowelplot_class.return_value = self.mock_vowelplot
        self.mock_vowelplot.data = MagicMock()
        self.mock_vowelplot.settings = MagicMock()

        VowelPlotPlotElement().begin()
        with DataPlotElement():
            pass

        self.mock_vowelplot.settings.pop.assert_called_once()
