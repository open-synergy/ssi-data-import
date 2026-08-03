# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .data_import_common import check_dotted_path


class DataImportTemplateMatcher(models.Model):
    """
    A single rule used to find the existing Target Model record a
    source file row corresponds to. The record's parent
    ``data_import_template`` combines every matcher line with the
    configured ``operator`` to build the search domain used to look up
    the record; ``value_code`` resolves the value compared against
    ``field_path`` from the current file row.
    """

    _name = "data_import_template.matcher"
    _description = "Data Import Template - Matcher"
    _order = "template_id, sequence"

    template_id = fields.Many2one(
        string="Template",
        comodel_name="data_import_template",
        required=True,
        ondelete="cascade",
        help="Data Import Template this matcher rule belongs to.",
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
        help="Determines the order the matcher rules are combined in "
        "and, when several rules read the same source column, the "
        "order they are listed in the tab.",
    )
    field_path = fields.Char(
        string="Field Path",
        required=True,
        help=(
            "Dot-separated path, starting from the Template's Target "
            "Model, of the field compared against Value Code (e.g. "
            "'partner_id.vat'). Free text rather than a field picker "
            "because it must be able to traverse relations that no "
            "single field record represents."
        ),
    )
    column = fields.Char(
        string="Column",
        required=True,
        help="Column name (or 0-based index when No Header Line is "
        "checked on the Template) read from the source file row.",
    )
    operator = fields.Selection(
        string="Operator",
        selection=[
            ("=", "="),
            ("!=", "!="),
            ("ilike", "contains"),
            ("in", "in"),
            (">=", ">="),
            ("<=", "<="),
        ],
        default="=",
        help="Domain operator used to compare Field Path against the "
        "value resolved by Value Code.",
    )
    value_code = fields.Text(
        string="Value Code",
        help=(
            "Python expression that resolves to the value compared "
            "against Field Path. Available variables:\n"
            "  - env, document, time, datetime, dateutil, timezone, "
            "float_compare, b64encode, b64decode\n"
            "  - row: dict of the current file row, keyed by column\n"
            "  - value: raw value of Column in the current row"
        ),
    )
    required = fields.Boolean(
        string="Required",
        default=True,
        help="If checked, a row with an empty value for Column is "
        "rejected instead of being matched with a partial rule.",
    )

    @api.constrains("field_path", "template_id")
    def _check_field_path(self):
        """Reject a ``field_path`` that does not resolve on the target.

        Delegates to ``check_dotted_path``, walking every dot-separated
        segment of ``field_path`` against the Template's
        ``model_id.model`` fields. Skipped when the Template has no
        Target Model yet.

        :raises ValidationError: when a segment of ``field_path`` does
            not exist on the resolved model
        """
        for rec in self:
            if not rec.template_id or not rec.template_id.model_id:
                continue
            check_dotted_path(
                rec.env,
                rec.template_id.model_id.model,
                rec.field_path,
                "Field Path",
            )
