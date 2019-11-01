"""
AWAD base request test.
"""

import pytest
import settings

from pyawad.util import updated
from pyawad.request import BaseRequest


@pytest.fixture
def default_params():
    return dict(Partner=settings.API.partner_code, Language=settings.DEFAULT_LANGUAGE)


@pytest.fixture
def req():
    return BaseRequest()


def test_is_unused(req):
    """ Test unused class. """
    assert req.is_unused is True


def test_is_failed(req):
    """ Test unused class. """
    assert req.is_failed is False


def test_default_params(req, default_params):
    """ Test default request params. """
    assert req.build_params() == default_params


def test_extra_params(req, default_params):
    """ Test default request params. """
    extra = { 'extra_key': 'extra_value' }
    params = updated(default_params, **extra)

    assert req.build_params(**extra) == params
