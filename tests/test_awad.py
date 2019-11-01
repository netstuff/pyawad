"""
Anywayanyday.com API integration tests.
"""

import pytest
import re

from datetime import datetime

from pyawad.request import (RouteRequest, FareRequest, RequestException)


DEPARTURE_DATE = datetime.now()
IATA_DEPARTURE = 'MOW'
IATA_ARRIVAL = 'LON'


class TestRouteSuccess:
    """
    Test route request success creation, status and response details.
    """
    AD = 1
    CN = 0
    IN = 0

    @pytest.fixture()
    async def route(cls):
        """ Create test route. """
        return await RouteRequest(
            date=DEPARTURE_DATE,
            departure=IATA_DEPARTURE,
            arrival=IATA_ARRIVAL,
            adults=cls.AD,
            childs=cls.CN,
            infants=cls.IN,
        ).create()

    @pytest.fixture()
    async def fares(cls, route):
        """ Route fares without fetched data (only identifiers). """
        return [fare async for fare in route.find_fares()]

    @pytest.mark.asyncio
    async def test_route_create(cls, route):
        """ Create remote route request and get its identity. """
        assert route.uid is not None
        assert re.match(r'\d+', route.uid)


    @pytest.mark.asyncio
    async def test_route_fetch(cls, route):
        """ Load route request data and test response data. """
        assert route.error is None
        assert route.uid is not None

        await route.fetch()
        assert route.response is not None

    @pytest.mark.asyncio
    async def test_fetch_fares(cls, fares):
        """ Find fares identifiers by route. """
        assert len(fares)

        for fare in fares:
            await fare.fetch()

            assert fare.amount is not None
            assert fare.currency is not None

            assert fare.adults is not None
            assert fare.infants is not None
            assert fare.children is not None


class TestRouteFailure:
    """
    Test invalid route requests.
    """
    # TODO: switch to parametrized tests.
    @pytest.mark.asyncio
    async def test_wrong_arrival(cls):
        """ Test request exception on same departure and arrival cities. """
        request = RouteRequest(date=DEPARTURE_DATE, departure=IATA_DEPARTURE, arrival='')

        try:
            await request.create()
            return False

        except RequestException as e:
            assert e.type == 'DirectionsAreEmpty'
