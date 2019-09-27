"""
Tests for settings.py
~~~~~~~~~~~~~~~~~~~~~
"""

import unittest

from vlnm.plotting.settings import Settings


class TestSettings(unittest.TestCase):
    """Tests for the Settings class."""

    def test_init(self):
        """Should init with initial scope."""
        settings = Settings()
        self.assertEqual(len(settings.scopes), 1)
        self.assertEqual(settings.state, {})

    def test_init(self):
        """Should init with initial settings."""
        state = dict(item='value')
        settings = Settings(state)
        self.assertEqual(len(settings.scopes), 1)
        self.assertEqual(settings.state, state)

    def test_push(self):
        """Should push settings onto stack in current scope."""
        settings = Settings()
        state = dict(item='value')
        settings.push(state)

        self.assertEqual(len(settings.scopes), 1)
        self.assertEqual(len(settings.stack), 2)
        self.assertEqual(settings.state, state)

    def test_push_with_merge(self):
        """Should merge settings onto stack in current scope."""
        settings = Settings(dict(item1='value1', item2='value2'))
        state = dict(item2='value3')
        settings.push(state)

        self.assertEqual(len(settings.scopes), 1)
        self.assertEqual(len(settings.stack), 2)
        self.assertEqual(len(settings.state), 2)
        self.assertEqual(settings.state['item2'], state['item2'])

    def test_pop_after_merge(self):
        """Should return previous settings in current scope."""
        state1 = dict(item1='value1', item2='value2')
        settings = Settings(state1)
        state2 = dict(item2='value3')
        settings.push(state2)

        self.assertEqual(len(settings.scopes), 1)
        self.assertEqual(len(settings.stack), 2)
        self.assertEqual(len(settings.state), 2)
        self.assertEqual(settings.state['item2'], state2['item2'])

        settings.pop()
        self.assertEqual(len(settings.stack), 1)
        self.assertEqual(len(settings.state), 2)
        self.assertEqual(settings.state, state1)

    def test_begin_scope(self):
        """New scope should copy the last state of the parent scope."""
        state = dict(item1='value1', item2='value2')
        settings = Settings(state)

        settings.begin_scope()

        self.assertEqual(len(settings.scopes), 2)
        self.assertEqual(len(settings.stack), 2)
        self.assertEqual(settings.stack[0], state)
        self.assertNotEqual(id(settings.stack[0]), id(state))

    def test_end_scope(self):
        """Should restore scope."""
        state = dict(item1='value1', item2='value2')
        settings = Settings(state)

        self.assertEqual(settings.state['item2'], 'value2')

        settings.begin_scope(dict(item2='value3'))

        self.assertEqual(settings.state['item2'], 'value3')

        settings.end_scope()

        self.assertEqual(settings.state['item2'], 'value2')
