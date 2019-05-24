import pytest
from xmlschema import XMLSchema
from pyawad.util import load_schema


class TestResponseSchemas:
  """ Test XML-schemas for validating AWAD response. """

  def test_new_request(self):
    """ Scheme on request created. """
    schema = load_schema('pyawad/schemas/response/NewRequest.xsd')

  def test_request_info(self):
    """ Scheme on getting created request info. """
    schema = load_schema('pyawad/schemas/response/RequestInfo.xsd')

  def test_request_state(self):
    """ Scheme on getting created request status. """
    schema = load_schema('pyawad/schemas/response/RequestState.xsd')

  def test_search_fares(self):
    """ Scheme on getting request searching results. """
    schema = load_schema('pyawad/schemas/response/Fares.xsd')
