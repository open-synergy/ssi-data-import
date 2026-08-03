# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDataImportApply(YamlTransactionCase):
    """Scenario tests for Apply: write/stale/error and O2M Upsert."""

    def test_apply(self):
        """Run the write/stale/rollback/cancel Apply scenarios."""
        self.run_yaml_scenario("test_data_import_apply.yaml")

    def _create_template_and_line(self, partner, action_vals, row):
        """Build a one-line document ready for Resolve, for O2M tests.

        :param partner: the ``res.partner`` Target Model record
        :param action_vals: ``vals`` dict for the single O2M Upsert
            ``data_import_template.action`` record
        :param row: dict written as this line's JSON ``data``
        :return: the created ``data_import.data`` line, after Resolve
        """
        template = self.env["data_import_template"].create(
            {
                "name": "O2M Upsert Template",
                "code": "/",
                "model_id": self.env.ref("base.model_res_partner").id,
                "on_no_match": "error",
                "on_multi_match": "error",
                "matcher_ids": [
                    (
                        0,
                        0,
                        {
                            # "ref" -- not "vat" -- because Odoo's
                            # commercial-fields sync
                            # (res.partner._commercial_fields())
                            # copies "vat" from a partner down to
                            # every non-company child created under
                            # it, which would make this matcher find
                            # more than one record once a child
                            # exists.
                            "field_path": "ref",
                            "column": "ref",
                            "operator": "=",
                            "required": True,
                        },
                    )
                ],
                "action_ids": [(0, 0, action_vals)],
            }
        )
        document = self.env["data_import"].create({"template_id": template.id})
        line = self.env["data_import.data"].create(
            {
                "import_id": document.id,
                "sequence": 10,
                "data": json.dumps(row),
            }
        )
        document.action_resolve()
        self.assertEqual(line.state, "matched")
        return line

    def test_o2m_upsert_creates_new_line(self):
        """O2M Upsert creates exactly one new line when none matches.

        P3/L-06: One2many comparison in ``odoo-yaml-test`` is set-based
        (order and per-row field content cannot be asserted), and
        ``REC:`` forbids subscripting -- the newly created child
        contact is never registered under a YAML alias, so its
        ``name``/``type`` can only be read back in Python.
        """
        partner = self.env["res.partner"].create(
            {"name": "O2M Upsert Partner One", "ref": "O2MREF001"}
        )
        self.assertFalse(partner.child_ids)
        line = self._create_template_and_line(
            partner,
            {
                "action_type": "o2m_upsert",
                "field_name": "child_ids",
                "relation_field": "type",
                "column": "child_name",
                "key_code": "'invoice'",
                "vals_code": "{'name': value, 'type': 'invoice'}",
            },
            {"ref": "O2MREF001", "child_name": "New Invoice Contact"},
        )
        line._apply()
        self.assertEqual(line.state, "done")
        invoice_children = partner.child_ids.filtered(lambda c: c.type == "invoice")
        self.assertEqual(len(invoice_children), 1)
        self.assertEqual(invoice_children.name, "New Invoice Contact")

    def test_o2m_upsert_updates_existing_line(self):
        """O2M Upsert updates the one line matching Key Code in place.

        P3/L-06: same reasoning as
        ``test_o2m_upsert_creates_new_line`` -- verifying the line
        count stayed at one *and* its name changed needs Python.
        """
        partner = self.env["res.partner"].create(
            {"name": "O2M Upsert Partner Two", "ref": "O2MREF002"}
        )
        existing_child = self.env["res.partner"].create(
            {
                "name": "Old Invoice Contact",
                "type": "invoice",
                "parent_id": partner.id,
            }
        )
        line = self._create_template_and_line(
            partner,
            {
                "action_type": "o2m_upsert",
                "field_name": "child_ids",
                "relation_field": "type",
                "column": "child_name",
                "key_code": "'invoice'",
                "vals_code": "{'name': value, 'type': 'invoice'}",
            },
            {"ref": "O2MREF002", "child_name": "Renamed Invoice Contact"},
        )
        line._apply()
        self.assertEqual(line.state, "done")
        invoice_children = partner.child_ids.filtered(lambda c: c.type == "invoice")
        self.assertEqual(len(invoice_children), 1)
        self.assertEqual(invoice_children, existing_child)
        self.assertEqual(invoice_children.name, "Renamed Invoice Contact")
