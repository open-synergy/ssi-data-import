# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDataImport(YamlTransactionCase):
    """Scenario tests for ``data_import`` creation and its guards."""

    def test_data_import(self):
        """Run the CRUD and negative path scenarios for the document."""
        self.run_yaml_scenario("test_data_import.yaml")

    def test_resolve(self):
        """Run the Resolve and conflict-detection scenarios."""
        self.run_yaml_scenario("test_data_import_resolve.yaml")
