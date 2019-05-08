"""
AWAD API requester.
"""

import aiohttp
import asyncio
import settings
import xml.etree.ElementTree as ETree

from datetime import datetime

from pyawad.util import updated


class RequestException(Exception):
  """ Base AWAD API request exception. """
  _request = None

  def __init__(self, request):
    self._request = request
    # TODO: switch type to base exception inheritance.
    self.type = request.error


class RequestNotCreated(RequestException):
  """ If request is not created. """
  pass


class RequestAttemptsExceeded(RequestException):
  """ If request progress status loading attempts is exceed. """
  pass


class BaseRequest:
  """
  Base request class to operate with AWAD API web-service.
  """

  # Public properties.
  error = None
  endpoint = None
  response = None

  # Protected properties.
  _id = None
  _client = None

  def __init__(self, _id=None, **kwargs):
    self.uid = _id

  @property
  def uid(self):
    """ Remote request identity. """
    return self._id

  @uid.setter
  def uid(self, value):
    """ Set request identity. """
    self._id = str(value).strip() if value else None

  @property
  def is_unused(self):
    """ Current request has never been executed. """
    return self.uid is None

  @property
  def is_failed(self):
    """ Current request is failed. """
    return self.error is not None

  @property
  def client(self):
    """ Current client session. """
    if not self._client or self._client.closed:
      self._client = aiohttp.ClientSession()

    return self._client

  @classmethod
  def get_url(cls, endpoint=None):
    """ Get API url to request data. """
    if endpoint is None:
      if not cls.endpoint:
        raise ValueError('Endpoint for {} not found'.format(cls.__name__))

      endpoint = cls.endpoint

    if not endpoint.endswith('/'):
      endpoint = endpoint + '/'

    return '{0.schema}://{0.host}/{1}'.format(settings.API, endpoint)

  def build_params(self, **kwargs):
    """ Get request params. """
    return updated(
      kwargs,
      Partner=settings.API.partner_code,
      Language=settings.DEFAULT_LANGUAGE
    )

  async def _request(self, url=None, params=None, **kwargs):
    """ Make request to remote API. """
    url = self.get_url(endpoint=url) if url is None or '/' not in url else url
    params = params or {}
    params = self.build_params(**params)

    try:
      async with self.client.get(url, params=params) as response:
        content = await response.read()
        etree = ETree.fromstring(content)
        error = etree.attrib.get('Error')

        if error:
          self.error = error
          self.response = None
          raise RequestException(self)
        else:
          self.response = etree

        return etree

    except aiohttp.ClientError as error:
      self.error = error

    finally:
      await self._teardown()

  async def _teardown(self):
    """ Close connection to remote API. """
    if self._client:
      if not self._client.closed:
        await self._client.close()

      self._client = None


class RouteRequest(BaseRequest):
  """
  Request for searching by route between two points.
  Result includes list of directions within.
  Request identity using for searching AWAD fares.
  """

  STATUS_TIMEOUT = 2
  STATUS_ATTEMPTS = 10

  _id = None
  _progress = 0
  _attempts = 0

  # Route info.
  departure_at = None
  departure_from = None
  arrival_to = None
  service_class = None

  # Passengers info.
  num_adult = None
  num_child = None
  num_infant = None

  def __init__(self, date, departure, arrival, adults=1, childs=0, infants=0, service_class='E', **kwargs):
    super().__init__(**kwargs)

    self.departure_at = date
    self.departure_from = departure
    self.arrival_to = arrival
    self.num_adult = adults
    self.num_child = childs
    self.num_infant = infants
    self.service_class = service_class

  @property
  def attempts(self):
    """ Attempts to get request status as totaly loaded. """
    return self._attempts

  @attempts.setter
  def attempts(self, value):
    if value > self.STATUS_ATTEMPTS:
      raise RequestAttemptsExceeded(self)

    self._attempts = value

  @property
  def is_completed(self):
    """ Flag which indicate tha current search request status is completed. """
    return self._progress == 100

  @property
  def serialized(self):
    """ Get route details serialized to string. """
    return '{0}{1}{2}'.format(
      self.departure_at.strftime('%d%m'),
      self.departure_from,
      self.arrival_to,
    )

  @property
  def status_timeout(self):
    """ Calculate wating time for next status requesting. """
    return self.STATUS_TIMEOUT

  def build_params(self, **kwargs):
    """ Get route request params. """
    return updated(
      super().build_params(**kwargs),

      Route=self.serialized,
      AD=self.num_adult,
      CN=self.num_child,
      IN=self.num_infant,
      SC=self.service_class,
    )

  async def create(self, **kwargs):
    """ Send request to remote for create new request. """
    if self.uid:
      # TODO: switch to pyawad exception.
      raise Exception('AWAD request which has identity cannot be created. Use "fetch" instead.')

    response = await self._request('NewRequest')

    if response is None:
      raise RequestNotCreated(self)

    self.uid = response.attrib.get('Id')

    return self

  async def find_fares(self, autoload=False):
    """ Find fares identifiers by passed route. """
    await self.wait()

    params = { 'R': self.uid }
    response = await self._request('Fares', params=params)

    for F in response.findall('F'):
      fare = FareRequest(F.attrib.get('Id'), self)

      if autoload is True:
        await fare.fetch()

      yield fare

  async def fetch(self):
    """ Load request info. """
    if not self.uid:
      # TODO: switch to pyawad exception.
      raise Exception('You must create AWAD request before fetching it.')

    params = { 'R': self.uid }
    response = await self._request('RequestInfo', params=params)

  async def status(self):
    """ Load request search progress status. """
    if not self.uid:
      # TODO: switch to pyawad exception.
      raise Exception('You must create AWAD request before fetching it.')

    if self.is_completed is not True:
      params = { 'R': self.uid }
      response = await self._request('RequestState', params=params)
      progress = int(response.attrib.get('Completed'))

      self._progress = progress

    return self._progress

  async def wait(self):
    """ Wait for loading request. """
    prev_status = self._progress

    while self._progress < 100:
      status = await self.status()
      await asyncio.sleep(self.STATUS_TIMEOUT)

      # If status not changed before neighboring attempts, increase attempts counter.
      if status == prev_status:
        self.attempts = self.attempts + 1

    return self


class FareRequest(BaseRequest):
  """
  Searching for fares request.
  Returns list of fares which ever should to be fetched.
  """

  _route_request = None

  # Fare attributes.
  _amount = None
  _currency = None
  is_available = None
  seats = None

  # Passengers.
  adults = None
  infants = None
  children = None


  def __init__(self, _id, request, **kwargs):
    super().__init__(_id=_id)
    self._route_request = request

  @property
  def request(self):
    return self._route_request

  def build_params(self, **kwargs):
    """ Get route request params. """
    return updated(
      super().build_params(**kwargs),
      R=self.request.uid,
    )

  async def fetch(self):
    """ Fetch fare data. """
    params = { 'F': self._id }
    response = await self._request('Fare', params=params)
    seats = response.attrib.get('MinAvailSeats', 'unknown')

    # Get fare attributes.
    self.amount = int(response.attrib.get('TotalAmount'))
    self.currency = response.attrib.get('Currency')
    self.is_available = response.attrib.get('Available') == 'True'
    self.seats = int(seats) if seats != 'unknown' else None

    # Get passengers.
    passengers = response.find('Passengers')
    self.adults = passengers.attrib.get('Adults')
    self.infants = passengers.attrib.get('Infants')
    self.children = passengers.attrib.get('Children')
