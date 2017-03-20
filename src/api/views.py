"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

import auth
from api.apikeyhandler import ApiKeyHandler
from api.rancher import Rancher
from api.serializers import KeySerializer
from api.utils import get_sciper
from config.settings import base


@api_view()
def api_root(request, format=None):
    return Response({
        'apikeys': reverse('apikeys', request=request, format=format),
        'schemas': reverse('schemas', request=request, format=format),
        'version': reverse('version', request=request, format=format)
    })


class CommonView(APIView):

    def __init__(self):

        self.apikey_handler = ApiKeyHandler()
        self.rancher = Rancher()
        self.authenticator = auth.get_configured_authenticator()


class KeysView(CommonView):

    def get_serializer(self):
        return KeySerializer

    def get(self, request):

        """
        Returns the user's API keys
        """

        # first we check the key
        username = self.apikey_handler.validate(
            request.GET.get('access_key', None),
            request.GET.get('secret_key', None)
        )
        if username:
            keys = self.apikey_handler.get_keys(username)
            return Response(keys, status=status.HTTP_200_OK)

        return Response("Invalid APIKey", status=status.HTTP_403_FORBIDDEN)

    def post(self, request):

        """
        Create a new API key
        """

        data = request.data

        import sys

        if self.authenticator.authenticate(data['username'], data['password']):

            the_key = self.apikey_handler.generate_keys(data['username'])

            serializer = KeySerializer(data=the_key.get_values())

            serializer.is_valid()

        else:
            return Response("Invalid APIKey", status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

        # data = JSONParser().parse(request)
        #
        # if self.authenticator.authenticate(data['username'], data['password']):
        #     the_key = self.apikey_handler.generate_keys(data['username'])
        #     return Response(the_key.get_values(), status=status.HTTP_200_OK)
        # else:
        #     return Response("Authentication failed", status=status.HTTP_401_UNAUTHORIZED)


class SchemasView(CommonView):

    def get(self, request):

        """
        Returns the user's schemas

        """

        username = self.apikey_handler.validate(
            request.GET.get('access_key', None),
            request.GET.get('secret_key', None)
        )
        if username:
            sciper = get_sciper(username)
            stacks = self.rancher.get_schemas(sciper)
            return Response(stacks, status=status.HTTP_200_OK)

        return Response("Invalid APIKey", status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        """
        Create a new schema
        """

        data = JSONParser().parse(request)

        username = self.apikey_handler.validate(
            data.get('access_key', None),
            data.get('secret_key', None)
        )

        if username:

            response = {}

            sciper = get_sciper(username)

            data = self.rancher.create_mysql_stack(sciper)
            response["connection_string"] = data["connection_string"]
            response["mysql_cmd"] = data["mysql_cmd"]

            return Response(response, status=status.HTTP_200_OK)

        return Response("Invalid APIKeys", status=status.HTTP_403_FORBIDDEN)


class VersionView(APIView):

    def get(self, request):

        """
        Returns the current API version
        """

        return Response(base.VERSION, status=status.HTTP_200_OK)
