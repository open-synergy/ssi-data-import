# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiDataImport(HttpSavepointCase):
    """Tour tests for the ``data_import`` work instructions."""

    @classmethod
    def setUpClass(cls):
        """Grant the user group and prepare every fixture the tours pick.

        Import File is intentionally never uploaded by any of these
        documents -- see the comment in ``data_import_tour.js`` -- so
        every one of them has zero Data lines. That keeps the
        Confirm/Approve/Cancel tours deterministic: with nothing for
        Apply to enqueue, Queue To Done falls straight through to Done
        in the same request as Approve, with no queue worker involved.
        Whether Load Data/Resolve/Apply actually process real rows is
        covered by the other test files instead.
        """
        super().setUpClass()
        admin_user = cls.env.ref("base.user_admin")
        # Pre-Condition: the Data Imports menu is gated by the user
        # group. Without it the tour dies on its first step -- the
        # menu is never rendered. base.user_admin is already a member
        # via ssi_data_import.data_import_validator_group's security
        # data, but this stays explicit and harmless if that changes.
        cls.env.ref("ssi_data_import.data_import_user_group").sudo().write(
            {"users": [(4, admin_user.id)]}
        )
        cls.env["data_import_template"].sudo().create(
            {
                "name": "Tour Import Template",
                "code": "/",
                "model_id": cls.env.ref("base.model_res_partner").id,
            }
        )

        # Every data_import document below is created with sudo() --
        # cls.env itself runs as SUPERUSER_ID, and the "Internal
        # Users" ir.rule (security/ir_rule/data_import.xml) only
        # shows a document to its own user_id. Without user_id
        # explicitly set to admin here, these documents default
        # user_id to SUPERUSER_ID and admin's tour would see an empty
        # list at its very first "Open the record" step.

        # Pre-Condition for ssi_data_import_data_import_confirm: a Draft
        # document, untouched by the tour before Flow starts.
        confirm_template = (
            cls.env["data_import_template"]
            .sudo()
            .create(
                {
                    "name": "Tour Confirm Template",
                    "code": "/",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                }
            )
        )
        cls.env["data_import"].sudo().create(
            {"template_id": confirm_template.id, "user_id": admin_user.id}
        )

        # Pre-Condition for ssi_data_import_data_import_approve: already
        # Waiting for Approval, built the same way patterns.md §E
        # prepares Pre-Condition for an existing-record tour -- calling
        # the action directly in Python, not through the UI.
        approve_template = (
            cls.env["data_import_template"]
            .sudo()
            .create(
                {
                    "name": "Tour Approve Template",
                    "code": "/",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                }
            )
        )
        approve_document = (
            cls.env["data_import"]
            .sudo()
            .create({"template_id": approve_template.id, "user_id": admin_user.id})
        )
        approve_document.with_user(admin_user).action_confirm()

        # Pre-Condition for ssi_data_import_data_import_cancel: already
        # Done (zero Data lines, so Approve reaches Done synchronously),
        # plus a global-use Cancel Reason for the wizard's radio widget.
        cancel_template = (
            cls.env["data_import_template"]
            .sudo()
            .create(
                {
                    "name": "Tour Cancel Template",
                    "code": "/",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                }
            )
        )
        cancel_document = (
            cls.env["data_import"]
            .sudo()
            .create({"template_id": cancel_template.id, "user_id": admin_user.id})
        )
        cancel_document_as_admin = cancel_document.with_user(admin_user)
        cancel_document_as_admin.action_confirm()
        # approve_ok is a non-stored compute that only depends on
        # policy_template_id (see mixin.policy._compute_policy) --
        # not on the approval_ids that action_confirm() just created
        # -- so its cached (pre-confirm, False) value must be
        # invalidated here or action_approve_approval() below raises
        # "Document is not allowed to approve" even though admin is a
        # genuine approver.
        cancel_document_as_admin.invalidate_cache()
        cancel_document_as_admin.with_context(
            queue_job__no_delay=True
        ).action_approve_approval()
        cls.env["base.cancel_reason"].sudo().create(
            {
                "name": "Tour Cancel Reason",
                "code": "TOUR-CANCEL",
                "global_use": True,
            }
        )

    def test_create(self):
        """Run the create tour for ``data_import``.

        IK: docs/data_import/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_data_import_data_import_create",
            login="admin",
        )

    def test_confirm(self):
        """Run the confirm tour for ``data_import``.

        IK: docs/data_import/04-confirm.md
        """
        self.start_tour(
            "/web",
            "ssi_data_import_data_import_confirm",
            login="admin",
        )

    def test_approve(self):
        """Run the approve tour for ``data_import``.

        IK: docs/data_import/05-approve.md
        """
        self.start_tour(
            "/web",
            "ssi_data_import_data_import_approve",
            login="admin",
        )

    def test_cancel(self):
        """Run the cancel tour for ``data_import``.

        IK: docs/data_import/10-cancel.md
        """
        self.start_tour(
            "/web",
            "ssi_data_import_data_import_cancel",
            login="admin",
        )
