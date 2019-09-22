"""
Tests for settings.py
~~~~~~~~~~~~~~~~~~~~~
"""

import unittest

from vlnm.plotting.settings import Settings


class TestSettings(unittest.TestCase):
    """Tests for the Settings class."""

    def test_init(self):
        """Should init with empty stack."""
        settings = Settings()
        self.assertEqual(len(settings.stack), 0)

    def test_push(self):
        """Should add to stack"""
        settings = Settings()
        settings.push(data=dict(data='df', x='f1', y='f2'))

        self.assertEqual(len(settings.stack), 1)
        self.assertIn('data', settings.stack[0])

    def test_current(self):
        """Should return merged stack by name"""
        settings = Settings()
        settings.push(data=dict(data='df'))
        settings.push(data=dict(x='f2', y='f1'))

        current = settings.current()

        self.assertEqual(len(settings.stack), 2)
        self.assertIn('data', current)

        data = current['data']
        self.assertIn('data', data)
        self.assertIn('x', data)
        self.assertIn('y', data)

    def test_current_by_value(self):
        """Should return merged stack by named value"""
        settings = Settings()
        settings.push(data=0)
        settings.push(data=1)

        current = settings.current()
        self.assertEqual(len(settings.stack), 2)
        self.assertIn('data', current)
        data = current['data']
        self.assertEqual(data, 1)

    def test_current_by_name(self):
        """Should return merged stack by name"""
        settings = Settings()
        settings.push(data=dict(data='df'))
        settings.push(data=dict(x='f2', y='f1'))

        current = settings.current('data')

        self.assertEqual(len(settings.stack), 2)
        self.assertIn('data', current)
        self.assertIn('x', current)
        self.assertIn('y', current)

    def test_current_by_tuple(self):
        """Should return merged stack by multiple names"""
        settings = Settings()
        settings.push(a=dict(key='value-a'))
        settings.push(b=dict(key='value-b'))
        settings.push(c=dict(key='value-c'))

        current = settings.current(['a', 'b'])

        self.assertEqual(len(settings.stack), 3)
        self.assertIn('a', current)
        self.assertIn('b', current)
        self.assertNotIn('c', current)

    def test_current_by_named_value(self):
        """Should return merged stack by named value"""
        settings = Settings()
        settings.push(data=0)
        settings.push(data=1)

        current = settings.current('data')
        self.assertEqual(len(settings.stack), 2)
        self.assertEqual(current, 1)

    def test_scope_keywords(self):
        """Scope should update settings before and after."""
        settings = Settings()
        settings.push(data=0)
        with settings.scope(data=1):
            current = settings.current('data')
            self.assertEqual(current, 1)

        current = settings.current('data')
        self.assertEqual(current, 0)

    def test_scope(self):
        """Scope should update settings before and after."""
        settings = Settings()
        settings.push(dict(data=0))
        with settings.scope(dict(data=1)):
            current = settings.current('data')
            self.assertEqual(current, 1)

        current = settings.current('data')
        self.assertEqual(current, 0)
