# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IgnoreDataImportRow(models.TransientModel):
    """
    One-shot dialog to ignore a single problem ``data_import.data``
    line with a recorded reason. Opened from that line's Ignore
    button. Confirm requires Reason to be filled, writes it to
    ``ignore_reason``, and moves the line to state Ignored -- a
    terminal outcome this module never reverts, which is why the
    reason is mandatory: it is the only audit trail left behind.
    """

    _name = "ignore_data_import_row"
    _description = "Ignore Data Import Row"

    data_id = fields.Many2one(
        string="# Data",
        comodel_name="data_import.data",
        required=True,
        ondelete="cascade",
        help="The Data line being ignored.",
    )
    reason = fields.Text(
        string="Reason",
        help="Explanation recorded on the Data line's Ignore Reason.",
    )

    @api.model
    def default_get(self, fields_list):
        """Prefill the wizard with the Data line it was opened from.

        :param fields_list: field names requested by the client
        :return: dict of default values
        """
        res = super().default_get(fields_list)
        if self.env.context.get("active_model") == "data_import.data":
            active_id = self.env.context.get("active_id")
            if active_id:
                res["data_id"] = active_id
        return res

    def action_confirm(self):
        """Ignore the linked Data line using this wizard's Reason.

        :return: an ``ir.actions.act_window_close`` dict, closing
            the dialog
        """
        for record in self.sudo():
            record._confirm()
        return {"type": "ir.actions.act_window_close"}

    def _confirm(self):
        """Ignore the linked Data line using this wizard's Reason.

        :return: nothing
        """
        self.ensure_one()
        self.data_id._ignore(self.reason)
