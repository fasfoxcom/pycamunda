# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.processinst
import pycamunda.variable
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def test_variablesgetlist_params(engine_url):
    get_vars = pycamunda.processinst.VariablesGetList(
        url=engine_url, process_instance_id='anId', deserialize_values=True
    )

    assert get_vars.url == engine_url + '/process-instance/anId/variables'
    assert get_vars.query_parameters() == {'deserializeValues': 'true'}
    assert get_vars.body_parameters() == {}


@unittest.mock.patch('requests.Session.request')
def test_variablesgetlist_calls_requests(mock, engine_url):
    get_vars = pycamunda.processinst.VariablesGetList(
        url=engine_url, process_instance_id='anId', deserialize_values=True
    )
    get_vars()

    assert mock.called
    assert mock.call_args[1]['method'].upper() == 'GET'


@unittest.mock.patch('requests.Session.request', raise_requests_exception_mock)
def test_variablesgetlist_raises_pycamunda_exception(engine_url):
    get_vars = pycamunda.processinst.VariablesGetList(
        url=engine_url, process_instance_id='anId', deserialize_values=True
    )
    with pytest.raises(pycamunda.PyCamundaException):
        get_vars()


@unittest.mock.patch('requests.Session.request', not_ok_response_mock)
@unittest.mock.patch('pycamunda.variable.Variable', unittest.mock.MagicMock())
@unittest.mock.patch('pycamunda.base._raise_for_status')
def test_variablesgetlist_raises_for_status(mock, engine_url):
    get_vars = pycamunda.processinst.VariablesGetList(
        url=engine_url, process_instance_id='anId', deserialize_values=True
    )
    get_vars()

    assert mock.called


@unittest.mock.patch('requests.Session.request', unittest.mock.MagicMock())
def test_variablesgetlist_returns_dict(engine_url):
    get_vars = pycamunda.processinst.VariablesGetList(
        url=engine_url, process_instance_id='anId', deserialize_values=True
    )
    variables = get_vars()

    assert isinstance(variables, dict)
    assert all(isinstance(variable, pycamunda.variable.Variable) for variable in variables.values())
