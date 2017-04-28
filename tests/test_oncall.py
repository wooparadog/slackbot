#! /usr/bin/env python


import pytest
import redis
import mock
from bender.service import on_call_service


@pytest.fixture(autouse=True)
def redis_client_mock(request, monkeypatch):
    r = redis.StrictRedis()
    monkeypatch.setattr('bender.mybot.r', r)
    request.addfinalizer(lambda: r.flushall())


@pytest.fixture
def mock_week_number(monkeypatch):
    week_mock = mock.Mock()
    monkeypatch.setattr('bender.service.get_current_week_number', week_mock)
    return week_mock


@pytest.fixture
def fill_on_call():
    on_call_service.add_oncall('bender', '1@root.com 188888888')
    on_call_service.add_oncall('bender', '2@root.com 188888888')
    on_call_service.add_oncall('bender', '3@root.com 188888888')


@pytest.fixture
def team():
    return 'bender'


def test_add_on_call(team, mock_week_number, fill_on_call):
    mock_week_number.return_value = 1
    assert on_call_service.get_oncall(team) == '1@root.com 188888888'

    mock_week_number.return_value = 2
    assert on_call_service.get_oncall(team) == '2@root.com 188888888'

    on_call_service.add_oncall('bender', '3@root.com 188888888')
    on_call_service.add_oncall('bender', '4@root.com 188888888')

    assert on_call_service.get_oncall(team) == '2@root.com 188888888'

    mock_week_number.return_value = 3
    assert on_call_service.get_oncall(team) == '3@root.com 188888888'

    mock_week_number.return_value = 4
    assert on_call_service.get_oncall(team) == '4@root.com 188888888'


def test_new_loop_on_call(team, mock_week_number, fill_on_call):
    mock_week_number.return_value = 4
    assert on_call_service.get_oncall(team) == '1@root.com 188888888'

    mock_week_number.return_value = 5
    assert on_call_service.get_oncall(team) == '2@root.com 188888888'


def test_new_loop_with_new_mwmber(team, mock_week_number, fill_on_call):
    mock_week_number.return_value = 1
    on_call_service.get_oncall('bender')

    mock_week_number.return_value = 2
    on_call_service.get_oncall('bender')

    mock_week_number.return_value = 3
    on_call_service.get_oncall('bender')

    on_call_service.add_oncall('bender', '4@root.com 188888888')
    mock_week_number.return_value = 4
    assert on_call_service.get_oncall(team) == '4@root.com 188888888'

    mock_week_number.return_value = 5
    assert on_call_service.get_oncall(team) == '1@root.com 188888888'

    mock_week_number.return_value = 6
    assert on_call_service.get_oncall(team) == '2@root.com 188888888'
