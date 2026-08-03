# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDataImportTemplate(YamlTransactionCase):
    """Scenario tests for ``data_import_template`` and its lines."""

    def test_data_import_template(self):
        """Run the CRUD and negative path scenarios for the template."""
        self.run_yaml_scenario("test_data_import_template.yaml")
