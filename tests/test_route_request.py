"""
AWAD route request test.
"""
import pytest
import settings

from datetime import datetime
from pyawad.request import RouteRequest


DEPARTURE_DATE = datetime.now()
IATA_DEPARTURE = 'MOW'
IATA_ARRIVAL = 'LON'
NUM_ADULT = 2
NUM_CHILD = 0
NUM_INFANT = 0


@pytest.fixture
def req():
    """ Request instance. """
    return RouteRequest(
        date=DEPARTURE_DATE,
        departure=IATA_DEPARTURE,
        arrival=IATA_ARRIVAL,
        adults=NUM_ADULT,
        childs=NUM_CHILD,
        infants=NUM_INFANT,
    )


def test_url(req):
    """ Test url of request to AWAD API. """
    url = req.get_url('Endpoint')
    assert url == '{0.schema}://{0.host}/Endpoint/'.format(settings.API, req)


@pytest.fixture
def request_string():
    """ Request params serialized to string. """
    return '{}{}{}'.format(
        DEPARTURE_DATE.strftime('%d%m'),
        IATA_DEPARTURE,
        IATA_ARRIVAL,
    )


def test_serialized(req, request_string):
    """ Test serialized route request params. """
    assert req.serialized == request_string


def test_build_params(req, request_string):
    """ Test building route request default params. """
    req.build_params() == dict(
        Route=request_string,
        AD=NUM_ADULT,
        CN=NUM_CHILD,
        IN=NUM_INFANT,
        SC='E',
    )
