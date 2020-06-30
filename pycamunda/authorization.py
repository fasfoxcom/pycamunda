# -*- coding: utf-8 -*-

"""This module provides access to the authorization REST api of Camunda."""

from __future__ import annotations
import typing
import dataclasses
import enum
import datetime as dt

import requests

import pycamunda
import pycamunda.base
import pycamunda.resource
from pycamunda.request import QueryParameter, PathParameter, BodyParameter

URL_SUFFIX = '/authorization'


__all__ = ['AuthorizationType']


class AuthorizationType(enum.IntEnum):
    global_ = 0
    grant = 1
    revoke = 2


@dataclasses.dataclass
class Authorization:
    """Data class of authorization as returned by the REST api of Camunda."""
    id_: str
    type_: AuthorizationType
    permissions: typing.Tuple[str]
    user_id: str
    group_id: str
    resource_type: pycamunda.resource.ResourceType
    resource_id: str
    links: typing.Tuple[pycamunda.resource.Link] = None
    root_process_instance_id: str = None
    removal_time: dt.datetime = None

    @classmethod
    def load(cls, data) -> Authorization:
        authorization = cls(
            id_=data['id'],
            type_=data['type'],
            permissions=data['permissions'],
            user_id=data['userId'],
            group_id=data['groupId'],
            resource_type=pycamunda.resource.ResourceType(data['resourceType']),
            resource_id=data['resourceId']
        )
        try:
            authorization.links = tuple(
                pycamunda.resource.Link.load(data=link) for link in data['links']
            )
        except KeyError:
            pass
        try:
            authorization.removal_time = pycamunda.base.from_isoformat(data['removalTime'])
        except KeyError:
            pass
        try:
            authorization.root_process_instance_id = data['rootProcessInstanceId']
        except KeyError:
            pass

        return authorization


class GetList(pycamunda.base.CamundaRequest):

    id_ = QueryParameter('id')
    type_ = QueryParameter('type')
    user_id_in = QueryParameter('userIdIn')
    group_id_in = QueryParameter('groupIdIn')
    resource_type = QueryParameter('resourceType')
    resource_id = QueryParameter('resourceId')
    sort_by = QueryParameter(
        'sortBy',
        mapping={
            'resource_type': 'resourceType',
            'resource_id': 'resourceId'
        }
    )
    ascending = QueryParameter(
        'sortOrder',
        mapping={True: 'asc', False: 'desc'},
        provide=lambda self, obj, obj_type: vars(obj).get('sort_by', None) is not None
    )
    first_result = QueryParameter('firstResult')
    max_results = QueryParameter('maxResults')

    def __init__(
        self,
        url: str,
        id_: str = None,
        type_: typing.Union[str, AuthorizationType] = None,
        user_id_in: typing.Iterable[str] = None,
        group_id_in: typing.Iterable[str] = None,
        resource_type: typing.Union[str, pycamunda.resource.ResourceType] = None,
        resource_id: int = None,
        sort_by: str = None,
        ascending: bool = True,
        first_result: int = None,
        max_results: int = None
    ):
        """Query for a list of authorizations using a list of parameters. The size of the result set
        can be retrieved by using the Get Count request.

        :param url: Camunda Rest engine URL.
        :param id_: Filter by the id of the authorization.
        :param type_: Filter by the authorization type.
        :param user_id_in: Filter whether the user id is one of multiple ones.
        :param group_id_in: Filter whether the group id is one of multiple ones.
        :param resource_type: Filter by the resource type.
        :param resource_id: Filter by the resource id.
        :param sort_by: Sort the results by `id_`, `lock_expiration_time, `process_instance_id`,
                        `process_definition_key`, `tenant_id` or `task_priority`.
        :param ascending: Sort order.
        :param first_result: Pagination of results. Index of the first result to return.
        :param max_results: Pagination of results. Maximum number of results to return.
        """
        super().__init__(url=url + URL_SUFFIX)
        self.id_ = id_
        self.type_ = None
        if type_ is not None:
            self.type_ = AuthorizationType(type_)
        self.user_id_in = user_id_in
        self.group_id_in = group_id_in
        self.resource_type = None
        if type_ is not None:
            self.resource_type = pycamunda.resource.ResourceType(resource_type)
        self.resource_id = resource_id
        self.sort_by = sort_by
        self.ascending = ascending
        self.first_result = first_result
        self.max_results = max_results

    def __call__(self, *args, **kwargs) -> typing.Tuple[Authorization]:
        """Send the request."""
        params = self.query_parameters()
        try:
            response = requests.get(self.url, params=params)
        except requests.exceptions.RequestException:
            raise pycamunda.PyCamundaException()
        if not response:
            pycamunda.base._raise_for_status(response)

        return tuple(Authorization.load(auth_json) for auth_json in response.json())


class Count(pycamunda.base.CamundaRequest):

    id_ = QueryParameter('id')
    type_ = QueryParameter('type')
    user_id_in = QueryParameter('userIdIn')
    group_id_in = QueryParameter('groupIdIn')
    resource_type = QueryParameter('resourceType')
    resource_id = QueryParameter('resourceId')

    def __init__(
        self,
        url: str,
        id_: str = None,
        type_: typing.Union[str, AuthorizationType] = None,
        user_id_in: typing.Iterable[str] = None,
        group_id_in: typing.Iterable[str] = None,
        resource_type: typing.Union[str, pycamunda.resource.ResourceType] = None,
        resource_id: int = None,
    ):
        """Get the size of the result returned by the Get List request.

        :param url: Camunda Rest engine URL.
        :param id_: Filter by the id of the authorization.
        :param type_: Filter by the authorization type.
        :param user_id_in: Filter whether the user id is one of multiple ones.
        :param group_id_in: Filter whether the group id is one of multiple ones.
        :param resource_type: Filter by the resource type.
        :param resource_id: Filter by the resource id.
        """
        super().__init__(url=url + URL_SUFFIX + '/count')
        self.id_ = id_
        self.type_ = None
        if type_ is not None:
            self.type_ = AuthorizationType(type_)
        self.user_id_in = user_id_in
        self.group_id_in = group_id_in
        self.resource_type = None
        if type_ is not None:
            self.resource_type = pycamunda.resource.ResourceType(resource_type)
        self.resource_id = resource_id

    def __call__(self, *args, **kwargs) -> int:
        """Send the request."""
        params = self.query_parameters()
        try:
            response = requests.get(self.url, params=params)
        except requests.exceptions.RequestException:
            raise pycamunda.PyCamundaException()
        if not response:
            pycamunda.base._raise_for_status(response)

        return int(response.json()['count'])


class Get(pycamunda.base.CamundaRequest):

    id_ = PathParameter('id')

    def __init__(self, url: str, id_: str):
        """Get an authorization.

        :param url: Camunda Rest engine URL.
        :param id_: Id of the authorization.
        """
        super().__init__(url=url + URL_SUFFIX + '/{id}')
        self.id_ = id_

    def __call__(self, *args, **kwargs) -> Authorization:
        """Send the request."""
        try:
            response = requests.get(self.url)
        except requests.exceptions.RequestException:
            raise pycamunda.PyCamundaException()
        if not response:
            pycamunda.base._raise_for_status(response)

        return Authorization.load(data=response.json())


if __name__ == '__main__':
    url = 'http://localhost:8080/engine-rest'

    get_authorizations = GetList(url=url)
    authorizations = get_authorizations()

    get_authorization = Get(url=url, id_=authorizations[0].id_)
    authorization = get_authorization()

    print(authorization)
