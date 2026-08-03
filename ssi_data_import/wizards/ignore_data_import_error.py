# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IgnoreDataImportError(models.TransientModel):
    """
    One-shot dialog to ignore every problem line of a ``data_import``
    document at once, with one shared reason. Opened from the
    document's Ignore All button while it is Queue To Done. Confirm
    requires Reason to be filled and applies it to every line
    currently in a resolvable state (Draft, No Match, Multiple
    Matches, Conflict, Stale, Error) via
    ``data_import._ignore_all_problem_data``.
    """

    _name = "ignore_data_import_error"
    _description = "Ignore Data Import Error"

    import_id = fields.Many2one(
        string="# Import",
        comodel_name="data_import",
        required=True,
        ondelete="cascade",
        help="The Data Import document whose problem lines are ignored.",
    )
    reason = fields.Text(
        string="Reason",
        help="Explanation recorded on every ignored Data line.",
    )

    @api.model
    def default_get(self, fields_list):
        """Prefill the wizard with the document it was opened from.

        :param fields_list: field names requested by the client
        :return: dict of default values
        """
        res = super().default_get(fields_list)
        if self.env.context.get("active_model") == "data_import":
            active_id = self.env.context.get("active_id")
            if active_id:
                res["import_id"] = active_id
        return res

    def action_confirm(self):
        """Ignore every problem line of the linked document.

        :return: an ``ir.actions.act_window_close`` dict, closing
            the dialog
        """
        for record in self.sudo():
            record._confirm()
        return {"type": "ir.actions.act_window_close"}

    def _confirm(self):
        """Ignore every problem Data line, using this Reason.

        :return: nothing
        """
        self.ensure_one()
        self.import_id._ignore_all_problem_data(self.reason)
