# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged

# Each of the four ``data_import`` tours (create/confirm/approve/cancel)
# now lives in its own HttpSavepointCase, one browser-tour process per
# class, instead of the four running back-to-back inside a single
# TestUiDataImport. That used to intermittently crash CI with "TypeError:
# Cannot set properties of null (setting 'props')" at
# FieldWrapper.updateModifiersValue -- a list-to-form navigation race in
# Odoo 14.0's core JS that hit a different one of the four tours on
# different runs of the same commit. Splitting reduces the resource
# pressure on the single headless browser process that used to run all
# four tours in sequence. See open-synergy/ssi-data-import#11.


@tagged("post_install", "-at_install")
class TestUiDataImportCreate(HttpSavepointCase):
    """Tour test for creating a ``data_import`` document."""

    @classmethod
    def setUpClass(cls):
        """Grant the user group and create the template the tour picks."""
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

    def test_create(self):
        """Run the create tour for ``data_import``.

        IK: docs/data_import/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_data_import_data_import_create",
            login="admin",
        )


@tagged("post_install", "-at_install")
class TestUiDataImportConfirm(HttpSavepointCase):
    """Tour test for confirming a ``data_import`` document."""

    @classmethod
    def setUpClass(cls):
        """Grant the user group and create a Draft document to confirm.

        Import File is intentionally never uploaded -- see the comment
        in ``data_import_tour.js`` -- so the document has zero Data
        lines. That keeps the tour deterministic: with nothing for
        Apply to enqueue, there is no queue worker involved.
        """
        super().setUpClass()
        admin_user = cls.env.ref("base.user_admin")
        cls.env.ref("ssi_data_import.data_import_user_group").sudo().write(
            {"users": [(4, admin_user.id)]}
        )
        # Pre-Condition: a Draft document, untouched by the tour before
        # Flow starts.
        #
        # Created with sudo() -- cls.env itself runs as SUPERUSER_ID,
        # and the "Internal Users" ir.rule
        # (security/ir_rule/data_import.xml) only shows a document to
        # its own user_id. Without user_id explicitly set to admin
        # here, this document would default user_id to SUPERUSER_ID
        # and admin's tour would see an empty list at its very first
        # "Open the record" step.
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

    def test_confirm(self):
        """Run the confirm tour for ``data_import``.

        IK: docs/data_import/04-confirm.md
        """
        self.start_tour(
            "/web",
            "ssi_data_import_data_import_confirm",
            login="admin",
        )


@tagged("post_install", "-at_install")
class TestUiDataImportApprove(HttpSavepointCase):
    """Tour test for approving a ``data_import`` document."""

    @classmethod
    def setUpClass(cls):
        """Grant the user group and create a document pending approval.

        Built the same way patterns.md §E prepares Pre-Condition for an
        existing-record tour -- calling the action directly in Python,
        not through the UI. With zero Data lines (no file uploaded,
        same reasoning as the create tour), Apply has nothing to
        enqueue, so the tour reaches Done synchronously.
        """
        super().setUpClass()
        admin_user = cls.env.ref("base.user_admin")
        cls.env.ref("ssi_data_import.data_import_user_group").sudo().write(
            {"users": [(4, admin_user.id)]}
        )
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
            .create(
                {
                    "template_id": approve_template.id,
                    "user_id": admin_user.id,
                }
            )
        )
        approve_document.with_user(admin_user).action_confirm()

    def test_approve(self):
        """Run the approve tour for ``data_import``.

        IK: docs/data_import/05-approve.md
        """
        self.start_tour(
            "/web",
            "ssi_data_import_data_import_approve",
            login="admin",
        )


@tagged("post_install", "-at_install")
class TestUiDataImportCancel(HttpSavepointCase):
    """Tour test for cancelling a ``data_import`` document."""

    @classmethod
    def setUpClass(cls):
        """Grant the user group and create a Done document to cancel.

        Also creates a global-use Cancel Reason for the wizard's radio
        widget. The document reaches Done synchronously because it has
        zero Data lines (no file uploaded), so Approve does not need a
        queue worker to finish.
        """
        super().setUpClass()
        admin_user = cls.env.ref("base.user_admin")
        cls.env.ref("ssi_data_import.data_import_user_group").sudo().write(
            {"users": [(4, admin_user.id)]}
        )
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
            .create(
                {
                    "template_id": cancel_template.id,
                    "user_id": admin_user.id,
                }
            )
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

    def test_cancel(self):
        """Run the cancel tour for ``data_import``.

        IK: docs/data_import/10-cancel.md
        """
        self.start_tour(
            "/web",
            "ssi_data_import_data_import_cancel",
            login="admin",
        )
