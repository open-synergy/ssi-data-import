# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class DataImport(models.Model):
    """Data import document scoped to a single operating unit."""

    _name = "data_import"
    _inherit = [
        "data_import",
        "mixin.single_operating_unit",
    ]
