"""
Useful utils.
"""
import os
import xmlschema


def updated(d, **kwargs):
  """ Return updated clone of passed dict. """
  _d = d.copy()
  _d.update(kwargs)
  return _d


def load_schema(path):
  """ Load schema from file. """
  return xmlschema.XMLSchema(path)
