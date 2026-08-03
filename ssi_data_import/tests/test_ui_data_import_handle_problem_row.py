# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiDataImportHandleProblemRow(HttpSavepointCase):
    """Tour test for the ``data_import`` Handle Problem Data Row IK."""

    @classmethod
    def setUpClass(cls):
        """Prepare a Queue To Done document with one Error Data line.

        The Template's single Action is a deliberately-failing
        ``python`` action, so once Approve fans out Apply for the
        line (synchronously, via ``queue_job__no_delay``), it always
        lands on state Error and the document stays at Queue To Done
        -- the exact Pre-Condition the tour needs, built the same way
        ``test_data_import_apply.yaml``'s "Apply Rolls Back" scenario
        does.
        """
        super().setUpClass()
        admin_user = cls.env.ref("base.user_admin")
        # Pre-Condition: the Data Imports menu is gated by the user
        # group -- see test_ui_data_import.py for the same reasoning.
        cls.env.ref("ssi_data_import.data_import_user_group").sudo().write(
            {"users": [(4, admin_user.id)]}
        )
        template = (
            cls.env["data_import_template"]
            .sudo()
            .create(
                {
                    "name": "Tour Problem Row Template",
                    "code": "/",
                    "model_id": cls.env.ref("base.model_res_partner").id,
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
                                "sequence": 10,
                                "action_type": "python",
                                "python_code": (
                                    "raise ValueError(" "'Deliberate failure for tour')"
                                ),
                            },
                        )
                    ],
                }
            )
        )
        partner = (
            cls.env["res.partner"]
            .sudo()
            .create({"name": "Tour Problem Partner", "vat": "TOURPROBVAT1"})
        )
        document = (
            cls.env["data_import"]
            .sudo()
            .create({"template_id": template.id, "user_id": admin_user.id})
        )
        cls.env["data_import.data"].sudo().create(
            {
                "import_id": document.id,
                "sequence": 10,
                "data": ('{"vat": "TOURPROBVAT1", "name": "Should Not Matter"}'),
            }
        )
        document_as_admin = document.with_user(admin_user)
        document_as_admin.action_resolve()
        document_as_admin.action_confirm()
        # approve_ok is a non-stored compute cached (pre-confirm,
        # False) before action_confirm() above created approval_ids
        # -- must be invalidated or action_approve_approval() below
        # raises even though admin is a genuine approver. Same
        # reasoning as test_ui_data_import.py's cancel Pre-Condition.
        document_as_admin.invalidate_cache()
        document_as_admin.with_context(
            queue_job__no_delay=True
        ).action_approve_approval()
        document_as_admin.invalidate_cache()
        partner.invalidate_cache()

    def test_handle_problem_row(self):
        """Run the handle-problem-row tour for ``data_import``.

        IK: docs/data_import/14-handle-problem-data.md
        """
        self.start_tour(
            "/web",
            "ssi_data_import_data_import_handle_problem_row",
            login="admin",
        )
