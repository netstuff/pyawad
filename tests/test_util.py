"""
Test util.
"""

from pyawad.util import updated


def test_updated():
  """ Test updated dict. """
  d0 = { 'a': 1 }
  d1 = { 'b': 2 }

  assert updated(d0, **d1) == { 'a': 1, 'b': 2 }
  assert d0 == { 'a': 1 }
  assert d1 == { 'b': 2 }
