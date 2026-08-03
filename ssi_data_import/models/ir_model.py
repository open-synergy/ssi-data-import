# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrModel(models.Model):
    """
    Extends ``ir.model`` with a counter of active ``data_import_template``
    records targeting it, and a manual action that repairs its Import
    History / Start Import contextual actions binding
    (``data_import_template.binding_action_ids``) when it has drifted
    from what ``data_import_template.create()``/``write()``/
    ``unlink()`` would otherwise maintain automatically -- e.g. after
    one of the two actions was deleted by hand.
    """

    _inherit = "ir.model"

    data_import_template_count = fields.Integer(
        string="# Data Import Templates",
        compute="_compute_data_import_template_count",
        help="Number of active Data Import Templates targeting this model.",
    )

    def _compute_data_import_template_count(self):
        """Count active Data Import Templates per Target Model.

        :return: nothing; assigns ``data_import_template_count``
        """
        template_model = self.env["data_import_template"]
        for record in self:
            record.data_import_template_count = template_model.search_count(
                [("model_id", "=", record.id)]
            )

    def action_resync_data_import_binding(self):
        """Repair Import History / Start Import bindings for ``self``.

        Re-runs ``data_import_template._sync_model_binding_for_models``
        for every model in ``self``, re-creating any Import History or
        Start Import action that was deleted by hand, or removing one
        left over for a model no longer targeted by any active Data
        Import Template.

        :return: nothing
        """
        self.env["data_import_template"]._sync_model_binding_for_models(self)
