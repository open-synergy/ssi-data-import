# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class EditDataImportRow(models.TransientModel):
    """
    One-shot dialog to fix a single ``data_import.data`` line's raw
    JSON without discarding it. Opened from that line's Edit button,
    prefilled with its current ``data`` by ``default_get``. Confirm
    validates the new text is a JSON object, overwrites ``data``, and
    returns the line to state Draft -- it never runs Resolve or
    Apply itself, leaving that to the line's own Retry button.
    """

    _name = "edit_data_import_row"
    _description = "Edit Data Import Row"

    data_id = fields.Many2one(
        string="# Data",
        comodel_name="data_import.data",
        required=True,
        ondelete="cascade",
        help="The Data line being edited.",
    )
    data = fields.Text(
        string="Data",
        help="Raw JSON object to overwrite the Data line's Data with.",
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
                line = self.env["data_import.data"].browse(active_id)
                res["data_id"] = line.id
                res["data"] = line.data
        return res

    def action_confirm(self):
        """Overwrite the Data line's Data and return it to Draft.

        :return: an ``ir.actions.act_window_close`` dict, closing
            the dialog
        """
        for record in self.sudo():
            record._confirm()
        return {"type": "ir.actions.act_window_close"}

    def _confirm(self):
        """Apply this wizard's edited JSON to the linked Data line.

        :return: nothing
        """
        self.ensure_one()
        self.data_id._edit_json(self.data)
