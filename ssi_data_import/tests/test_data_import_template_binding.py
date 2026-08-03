# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDataImportTemplateBinding(YamlTransactionCase):
    """Scenario tests for the Import History / Start Import binding."""

    def test_data_import_template_binding(self):
        """Run the create/write/unlink binding sync scenarios."""
        self.run_yaml_scenario("test_data_import_template_binding.yaml")

    def test_resync_restores_deleted_binding_action(self):
        """Force-delete one binding action, then repair it via resync.

        Pure Python -- trigger P1 (L-01: ``action: call`` in YAML
        discards a method's return value, and
        ``ir.model.action_resync_data_import_binding`` returns
        nothing -- the only observable outcome of the repair it
        performs is a new ``ir.actions.act_window`` row, which this
        test re-searches for directly instead of asserting a return
        value that does not exist).
        """
        partner_model = self.env.ref("base.model_res_partner")
        binding_domain = [
            ("binding_model_id", "=", partner_model.id),
            ("res_model", "=", "data_import.data"),
            ("binding_type", "=", "action"),
        ]
        template = self.env["data_import_template"].create(
            {
                "name": "Binding Resync Template",
                "code": "/",
                "model_id": partner_model.id,
            }
        )
        history_action = self.env["ir.actions.act_window"].search(binding_domain)
        self.assertTrue(history_action)
        history_action.unlink()
        self.assertFalse(self.env["ir.actions.act_window"].search(binding_domain))

        partner_model.action_resync_data_import_binding()

        repaired_action = self.env["ir.actions.act_window"].search(binding_domain)
        self.assertTrue(repaired_action)
        self.assertIn(repaired_action, template.binding_action_ids)
