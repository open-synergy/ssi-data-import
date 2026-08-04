# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestDataImportOperatingUnit(YamlTransactionCase):
    """Scenario tests for the operating unit field on ``data_import``."""

    def test_data_import_operating_unit(self):
        """Run the operating unit assignment and default scenarios."""
        self.run_yaml_scenario("test_data_import_operating_unit.yaml")

    @mute_logger("odoo.sql_db")
    def test_operating_unit_invalid_reference(self):
        """Pure Python -- trigger P5 (L-22: `psycopg2.IntegrityError` is
        outside the 12 error types `expect_error` can name).

        ``data_import.operating_unit_id`` is a Many2one to
        ``operating.unit`` enforced by a DB-level foreign key. Writing a
        nonexistent id raises a raw `psycopg2.IntegrityError` at create
        time -- there is no YAML-expressible way to assert it.
        `mute_logger("odoo.sql_db")` silences the ERROR line PostgreSQL
        normally writes here; without it `oca_checklog_odoo` would fail
        CI even though the test passes.
        """
        partner_model = self.env.ref("base.model_res_partner")
        template = self.env["data_import_template"].create(
            {
                "name": "Import Template OU Invalid",
                "code": "/",
                "model_id": partner_model.id,
            }
        )
        last_ou = self.env["operating.unit"].search(
            [], order="id desc", limit=1
        )
        bogus_operating_unit_id = last_ou.id + 1000000
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            with self.cr.savepoint():
                self.env["data_import"].create(
                    {
                        "template_id": template.id,
                        "operating_unit_id": bogus_operating_unit_id,
                    }
                )
