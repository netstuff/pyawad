"""
Useful utils.
"""

def updated(d, **kwargs):
  """ Return updated clone of passed dict. """
  _d = d.copy()
  _d.update(kwargs)
  return _d
