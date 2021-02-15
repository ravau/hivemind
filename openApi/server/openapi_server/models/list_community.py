# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.community_context import CommunityContext
from openapi_server import util

from openapi_server.models.community_context import CommunityContext  # noqa: E501

class ListCommunity(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, about=None, admins=None, avatar_url=None, context=None, created_at=None, is_nsfw=None, lang=None, name=None, num_authors=None, num_pending=None, subscribers=None, sum_pending=None, title=None, type_id=None):  # noqa: E501
        """ListCommunity - a model defined in OpenAPI

        :param id: The id of this ListCommunity.  # noqa: E501
        :type id: int
        :param about: The about of this ListCommunity.  # noqa: E501
        :type about: str
        :param admins: The admins of this ListCommunity.  # noqa: E501
        :type admins: List[str]
        :param avatar_url: The avatar_url of this ListCommunity.  # noqa: E501
        :type avatar_url: str
        :param context: The context of this ListCommunity.  # noqa: E501
        :type context: CommunityContext
        :param created_at: The created_at of this ListCommunity.  # noqa: E501
        :type created_at: datetime
        :param is_nsfw: The is_nsfw of this ListCommunity.  # noqa: E501
        :type is_nsfw: bool
        :param lang: The lang of this ListCommunity.  # noqa: E501
        :type lang: str
        :param name: The name of this ListCommunity.  # noqa: E501
        :type name: str
        :param num_authors: The num_authors of this ListCommunity.  # noqa: E501
        :type num_authors: int
        :param num_pending: The num_pending of this ListCommunity.  # noqa: E501
        :type num_pending: int
        :param subscribers: The subscribers of this ListCommunity.  # noqa: E501
        :type subscribers: int
        :param sum_pending: The sum_pending of this ListCommunity.  # noqa: E501
        :type sum_pending: int
        :param title: The title of this ListCommunity.  # noqa: E501
        :type title: str
        :param type_id: The type_id of this ListCommunity.  # noqa: E501
        :type type_id: int
        """
        self.openapi_types = {
            'id': int,
            'about': str,
            'admins': List[str],
            'avatar_url': str,
            'context': CommunityContext,
            'created_at': datetime,
            'is_nsfw': bool,
            'lang': str,
            'name': str,
            'num_authors': int,
            'num_pending': int,
            'subscribers': int,
            'sum_pending': int,
            'title': str,
            'type_id': int
        }

        self.attribute_map = {
            'id': 'id',
            'about': 'about',
            'admins': 'admins',
            'avatar_url': 'avatar_url',
            'context': 'context',
            'created_at': 'created_at',
            'is_nsfw': 'is_nsfw',
            'lang': 'lang',
            'name': 'name',
            'num_authors': 'num_authors',
            'num_pending': 'num_pending',
            'subscribers': 'subscribers',
            'sum_pending': 'sum_pending',
            'title': 'title',
            'type_id': 'type_id'
        }

        self._id = id
        self._about = about
        self._admins = admins
        self._avatar_url = avatar_url
        self._context = context
        self._created_at = created_at
        self._is_nsfw = is_nsfw
        self._lang = lang
        self._name = name
        self._num_authors = num_authors
        self._num_pending = num_pending
        self._subscribers = subscribers
        self._sum_pending = sum_pending
        self._title = title
        self._type_id = type_id

    @classmethod
    def from_dict(cls, dikt) -> 'ListCommunity':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ListCommunity of this ListCommunity.  # noqa: E501
        :rtype: ListCommunity
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this ListCommunity.


        :return: The id of this ListCommunity.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this ListCommunity.


        :param id: The id of this ListCommunity.
        :type id: int
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def about(self):
        """Gets the about of this ListCommunity.


        :return: The about of this ListCommunity.
        :rtype: str
        """
        return self._about

    @about.setter
    def about(self, about):
        """Sets the about of this ListCommunity.


        :param about: The about of this ListCommunity.
        :type about: str
        """
        if about is None:
            raise ValueError("Invalid value for `about`, must not be `None`")  # noqa: E501

        self._about = about

    @property
    def admins(self):
        """Gets the admins of this ListCommunity.


        :return: The admins of this ListCommunity.
        :rtype: List[str]
        """
        return self._admins

    @admins.setter
    def admins(self, admins):
        """Sets the admins of this ListCommunity.


        :param admins: The admins of this ListCommunity.
        :type admins: List[str]
        """

        self._admins = admins

    @property
    def avatar_url(self):
        """Gets the avatar_url of this ListCommunity.


        :return: The avatar_url of this ListCommunity.
        :rtype: str
        """
        return self._avatar_url

    @avatar_url.setter
    def avatar_url(self, avatar_url):
        """Sets the avatar_url of this ListCommunity.


        :param avatar_url: The avatar_url of this ListCommunity.
        :type avatar_url: str
        """
        if avatar_url is None:
            raise ValueError("Invalid value for `avatar_url`, must not be `None`")  # noqa: E501

        self._avatar_url = avatar_url

    @property
    def context(self):
        """Gets the context of this ListCommunity.


        :return: The context of this ListCommunity.
        :rtype: CommunityContext
        """
        return self._context

    @context.setter
    def context(self, context):
        """Sets the context of this ListCommunity.


        :param context: The context of this ListCommunity.
        :type context: CommunityContext
        """
        if context is None:
            raise ValueError("Invalid value for `context`, must not be `None`")  # noqa: E501

        self._context = context

    @property
    def created_at(self):
        """Gets the created_at of this ListCommunity.


        :return: The created_at of this ListCommunity.
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this ListCommunity.


        :param created_at: The created_at of this ListCommunity.
        :type created_at: datetime
        """
        if created_at is None:
            raise ValueError("Invalid value for `created_at`, must not be `None`")  # noqa: E501

        self._created_at = created_at

    @property
    def is_nsfw(self):
        """Gets the is_nsfw of this ListCommunity.


        :return: The is_nsfw of this ListCommunity.
        :rtype: bool
        """
        return self._is_nsfw

    @is_nsfw.setter
    def is_nsfw(self, is_nsfw):
        """Sets the is_nsfw of this ListCommunity.


        :param is_nsfw: The is_nsfw of this ListCommunity.
        :type is_nsfw: bool
        """
        if is_nsfw is None:
            raise ValueError("Invalid value for `is_nsfw`, must not be `None`")  # noqa: E501

        self._is_nsfw = is_nsfw

    @property
    def lang(self):
        """Gets the lang of this ListCommunity.


        :return: The lang of this ListCommunity.
        :rtype: str
        """
        return self._lang

    @lang.setter
    def lang(self, lang):
        """Sets the lang of this ListCommunity.


        :param lang: The lang of this ListCommunity.
        :type lang: str
        """
        if lang is None:
            raise ValueError("Invalid value for `lang`, must not be `None`")  # noqa: E501

        self._lang = lang

    @property
    def name(self):
        """Gets the name of this ListCommunity.


        :return: The name of this ListCommunity.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this ListCommunity.


        :param name: The name of this ListCommunity.
        :type name: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def num_authors(self):
        """Gets the num_authors of this ListCommunity.


        :return: The num_authors of this ListCommunity.
        :rtype: int
        """
        return self._num_authors

    @num_authors.setter
    def num_authors(self, num_authors):
        """Sets the num_authors of this ListCommunity.


        :param num_authors: The num_authors of this ListCommunity.
        :type num_authors: int
        """
        if num_authors is None:
            raise ValueError("Invalid value for `num_authors`, must not be `None`")  # noqa: E501

        self._num_authors = num_authors

    @property
    def num_pending(self):
        """Gets the num_pending of this ListCommunity.


        :return: The num_pending of this ListCommunity.
        :rtype: int
        """
        return self._num_pending

    @num_pending.setter
    def num_pending(self, num_pending):
        """Sets the num_pending of this ListCommunity.


        :param num_pending: The num_pending of this ListCommunity.
        :type num_pending: int
        """
        if num_pending is None:
            raise ValueError("Invalid value for `num_pending`, must not be `None`")  # noqa: E501

        self._num_pending = num_pending

    @property
    def subscribers(self):
        """Gets the subscribers of this ListCommunity.


        :return: The subscribers of this ListCommunity.
        :rtype: int
        """
        return self._subscribers

    @subscribers.setter
    def subscribers(self, subscribers):
        """Sets the subscribers of this ListCommunity.


        :param subscribers: The subscribers of this ListCommunity.
        :type subscribers: int
        """
        if subscribers is None:
            raise ValueError("Invalid value for `subscribers`, must not be `None`")  # noqa: E501

        self._subscribers = subscribers

    @property
    def sum_pending(self):
        """Gets the sum_pending of this ListCommunity.


        :return: The sum_pending of this ListCommunity.
        :rtype: int
        """
        return self._sum_pending

    @sum_pending.setter
    def sum_pending(self, sum_pending):
        """Sets the sum_pending of this ListCommunity.


        :param sum_pending: The sum_pending of this ListCommunity.
        :type sum_pending: int
        """
        if sum_pending is None:
            raise ValueError("Invalid value for `sum_pending`, must not be `None`")  # noqa: E501

        self._sum_pending = sum_pending

    @property
    def title(self):
        """Gets the title of this ListCommunity.


        :return: The title of this ListCommunity.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this ListCommunity.


        :param title: The title of this ListCommunity.
        :type title: str
        """
        if title is None:
            raise ValueError("Invalid value for `title`, must not be `None`")  # noqa: E501

        self._title = title

    @property
    def type_id(self):
        """Gets the type_id of this ListCommunity.


        :return: The type_id of this ListCommunity.
        :rtype: int
        """
        return self._type_id

    @type_id.setter
    def type_id(self, type_id):
        """Sets the type_id of this ListCommunity.


        :param type_id: The type_id of this ListCommunity.
        :type type_id: int
        """
        if type_id is None:
            raise ValueError("Invalid value for `type_id`, must not be `None`")  # noqa: E501

        self._type_id = type_id
