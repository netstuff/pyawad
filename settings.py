import os


class API:
  """
  AWAD API settings.
  """

  schema = 'http'
  host = 'api.anywayanyday.com/api'
  partner_code = os.environ.get('AWAD_PARNTER_CODE', 'testapid')


# Default base requests parameters.
DEFAULT_CURRENCY = 'RUB'
DEFAULT_LANGUAGE = 'RU'
