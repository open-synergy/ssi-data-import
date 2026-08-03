# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDataImportHandleProblemRow(YamlTransactionCase):
    """Scenario tests for the Edit/Ignore/Ignore All/Retry wizards."""

    def test_handle_problem_row(self):
        """Run the Edit/Ignore/Retry scenarios."""
        self.run_yaml_scenario("test_data_import_handle_problem_row.yaml")

    def test_open_edit_wizard_returns_act_window(self):
        """The Edit button returns an act_window pointing at the wizard.

        P1/L-01: ``action: call`` in the YAML DSL discards a method's
        return value, so the ``ir.actions.act_window`` dict returned
        by ``action_open_edit_wizard`` -- the button that opens the
        Edit JSON wizard -- cannot be asserted from YAML and must be
        checked directly in Python instead.
        """
        template = self.env["data_import_template"].create(
            {
                "name": "Open Edit Wizard Template",
                "code": "/",
                "model_id": self.env.ref("base.model_res_partner").id,
            }
        )
        document = self.env["data_import"].create({"template_id": template.id})
        line = self.env["data_import.data"].create(
            {
                "import_id": document.id,
                "sequence": 10,
                "data": "{}",
            }
        )
        result = line.action_open_edit_wizard()
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "edit_data_import_row")
        self.assertEqual(result["target"], "new")
