"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import unittest
from time import sleep

from django.test import tag

from api import rancher
from api.tests import KERMIT_SCIPER, KERMIT_UNIT


class RancherTest(unittest.TestCase):

    def setUp(self):
        self.idevelop_id = "13030"

    @tag('rancher')
    def test_get(self):
        conn = rancher.Rancher()

        r = conn.get("/v1-catalog/templates/idevelop:mysql")

        self.assertEqual(200, r.status_code)

    @tag('rancher')
    def test_get_template(self):
        conn = rancher.Rancher()

        template = "idevelop:mysql"

        data = conn.get_template(template)

        self.assertTrue(data["id"].startswith(template))

    @tag('rancher')
    def test_create_mysql_stack(self):
        conn = rancher.Rancher()
        data = conn.create_mysql_stack(KERMIT_SCIPER, unit_id=self.idevelop_id)

        self.assertTrue(data["connection_string"].startswith("mysql://"))
        self.assertTrue(data["mysql_cmd"].startswith("mysql "))

        # Return stacks by sciper
        conn.get_stacks_by_user(KERMIT_SCIPER)

        # Clean stacks
        conn.clean_stacks(KERMIT_SCIPER)

    @tag('rancher')
    def test_get_ports_used(self):
        conn = rancher.Rancher()
        ports_used = conn.get_ports_used()
        self.assertTrue(ports_used, list)

    @tag('rancher')
    def test_get_available_port(self):
        conn = rancher.Rancher()
        conn.get_available_port()

    @tag('rancher')
    def test_get_stacks(self):
        # Create new stacks
        conn = rancher.Rancher()

        conn.create_mysql_stack(KERMIT_SCIPER, unit_id=self.idevelop_id)
        conn.create_mysql_stack(KERMIT_SCIPER, unit_id=self.idevelop_id)

        # Return stacks by sciper
        stacks = conn.get_stacks_by_user(KERMIT_SCIPER)

        # Check the number of stacks
        self.assertEqual(len(stacks), 2)

        # Clean stacks
        conn.clean_stacks(KERMIT_SCIPER)

    @tag('rancher')
    def test_get_schemas(self):
        # Create new stacks
        conn = rancher.Rancher()
        conn.create_mysql_stack(KERMIT_SCIPER, unit_id=self.idevelop_id)
        conn.create_mysql_stack(KERMIT_SCIPER, unit_id=self.idevelop_id)

        # Return schemas by sciper
        schemas = conn.get_schemas_by_user(KERMIT_SCIPER)

        # Check the number of stacks
        self.assertEqual(len(schemas), 2)

        # Return schemas by unit and user
        schemas = conn.get_schemas_by_unit_and_user(KERMIT_UNIT, KERMIT_SCIPER)

        # Check the number of stacks
        self.assertEqual(len(schemas), 2)

        # Return schemas by unit and user
        schemas = conn.get_schemas_by_unit(KERMIT_UNIT)

        # Check the number of stacks
        self.assertEqual(len(schemas), 2)

        # Return stacks by sciper
        conn.get_stacks_by_user(KERMIT_SCIPER)

        # Clean stacks
        conn.clean_stacks(KERMIT_SCIPER)

    @tag('rancher')
    def test_delete_schema(self):

        # Create and delete schema
        conn = rancher.Rancher()
        data = conn.create_mysql_stack(KERMIT_SCIPER, unit_id=self.idevelop_id)
        conn.delete_schema(data["schema_id"])

        sleep(15)

        # Return schemas by sciper
        schemas = conn.get_schemas_by_user(KERMIT_SCIPER)

        self.assertEqual(len(schemas), 0)

    @tag('rancher')
    def test_get_schema(self):

        conn = rancher.Rancher()
        data = conn.create_mysql_stack(KERMIT_SCIPER, unit_id=self.idevelop_id)

        schema = conn.get_schema(data["schema_id"])
        self.assertEqual(KERMIT_UNIT, schema["unit_id"])

        conn.delete_schema(data["schema_id"])
