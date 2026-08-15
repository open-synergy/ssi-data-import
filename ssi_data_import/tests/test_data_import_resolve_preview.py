# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDataImportResolvePreview(YamlTransactionCase):
    """Python-only scenario for Resolve's ``preview`` JSON payload.

    P4/L-07: ``preview`` is stored as a JSON-encoded ``Text`` field,
    so a specific key inside it can only be inspected by decoding the
    JSON in Python -- ``odoo-yaml-test``'s dotted-path assert walks
    plain ``getattr`` chains and cannot subscript into a parsed JSON
    dict.
    """

    def setUp(self):
        """Create a partner, a one-Action Template, and one Data line.

        The Template's single Write Field action targets the
        partner's ``name``, so Resolve is expected to preview both
        its current value (``before``) and the value read from the
        row (``after``).
        """
        super().setUp()
        self.partner = self.env["res.partner"].create(
            {"name": "Preview Partner", "vat": "RESOLVEPREVIEW001"}
        )
        self.template = self.env["data_import_template"].create(
            {
                "name": "Preview Template",
                "code": "/",
                "model_id": self.env.ref("base.model_res_partner").id,
                "on_no_match": "error",
                "on_multi_match": "error",
                "matcher_ids": [
                    (
                        0,
                        0,
                        {
                            "field_path": "vat",
                            "column": "vat",
                            "operator": "=",
                            "required": True,
                        },
                    )
                ],
                "action_ids": [
                    (
                        0,
                        0,
                        {
                            "action_type": "write",
                            "field_name": "name",
                            "column": "name",
                            "value_code": "value",
                            "skip_if_empty": False,
                        },
                    )
                ],
            }
        )
        self.document = self.env["data_import"].create(
            {"template_id": self.template.id}
        )
        self.line = self.env["data_import.data"].create(
            {
                "import_id": self.document.id,
                "sequence": 10,
                "data": json.dumps({"vat": "RESOLVEPREVIEW001", "name": "New Name"}),
            }
        )

    def test_preview_has_before_and_after_for_configured_action(self):
        """``preview`` carries before/after values for the Write action.

        P4/L-07: the JSON key ``name`` (the configured action's Field
        Name) can only be checked by decoding ``preview`` in Python.
        """
        self.document.action_resolve()
        self.assertEqual(self.line.state, "matched")
        preview = json.loads(self.line.preview)
        self.assertIn("name", preview)
        self.assertEqual(preview["name"]["before"], "Preview Partner")
        self.assertEqual(preview["name"]["after"], "New Name")
