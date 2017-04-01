"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""

import auth

from rest_framework import serializers

from .apikeyhandler import ApiKeyHandler
from .rancher import Rancher
from .utils import get_sciper, get_units


class KeySerializer(serializers.Serializer):
    """
    API Key Serializer
    """
    username = serializers.CharField(max_length=256)
    password = serializers.CharField(max_length=256)

    def validate(self, attrs):
        """
        Validate the user authentication
        """
        username = attrs.get('username')
        password = attrs.get('password')

        result = {}

        if username and password:

            authenticator = auth.get_configured_authenticator()

            if authenticator.authenticate(username=username, password=password):
                result["username"] = username

        if not result:
            raise serializers.ValidationError("Authentication failed", code='authorization')

        return result

    def create(self, validated_data):
        """
        Create the APIKeys
        """
        return ApiKeyHandler.generate_keys(validated_data["username"])


class SchemaSerializer(serializers.Serializer):
    """
    Schema Serializer
    """
    access_key = serializers.CharField(max_length=256)
    secret_key = serializers.CharField(max_length=256)
    unit = serializers.CharField(max_length=256, required=False)

    @staticmethod
    def _manage_units(username, unit, result):
        """
        Manage unit
        """
        # Return all the unit of user
        units = get_units(username)

        if not unit:
            if len(units) > 1:
                raise serializers.ValidationError("User has more one unit", code='invalid')
            if len(units) < 1:
                raise serializers.ValidationError("User has no unit", code='invalid')
            elif len(units) == 1:
                unit = units[0]
                result["unit"] = unit

        elif unit not in units:
            raise serializers.ValidationError("Bad unit", code='invalid')

        else:
            result["unit"] = unit
        return result

    def validate(self, attrs):
        """
        Validate the APIKeys and the unit (if the unit is given)
        """
        result = {}

        if self.partial:

            if 'unit' in attrs:
                unit = attrs.get('unit')
                result["unit"] = unit
            return result

        else:
            access_key = attrs.get('access_key')
            secret_key = attrs.get('secret_key')

            unit = None
            if 'unit' in attrs:
                unit = attrs.get('unit')

            username = ApiKeyHandler.validate(access=access_key, secret=secret_key)

            if username:
                result["username"] = username

                result = SchemaSerializer._manage_units(username, unit, result)

            if 'username' not in result or 'unit' not in result:
                raise serializers.ValidationError("Invalid APIKeys", code='invalid')

            return result

    def create(self, validated_data):
        """
        Now we have validated data. So we can create schema.
        """

        # Ldap search to find sciper from username
        sciper = get_sciper(validated_data["username"])

        unit = None
        if "unit" in validated_data:
            unit = validated_data['unit']

        schema = Rancher.create_mysql_stack(sciper, unit)

        return {
            "connection_string": schema["connection_string"],
            "mysql_cmd": schema["mysql_cmd"]
        }

    def update(self, schema_id, validated_data):
        """
        Now we have validated data. So we can update schema.
        """
        schema = Rancher.get_schema(schema_id)

        unit = None
        if "unit" in validated_data:
            unit = validated_data['unit']

        schema['unit'] = unit

        return schema
