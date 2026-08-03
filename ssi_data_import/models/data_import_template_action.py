# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .data_import_common import check_dotted_path


class DataImportTemplateAction(models.Model):
    """
    A single change applied to the Target Model record matched (or
    created) by the parent ``data_import_template``'s Matcher rules.
    ``action_type`` selects how the change is applied: a plain field
    write, a One2many upsert keyed by ``key_code``, a Many2many set
    operation, or an arbitrary Python statement.
    """

    _name = "data_import_template.action"
    _description = "Data Import Template - Action"
    _order = "template_id, sequence"

    template_id = fields.Many2one(
        string="Template",
        comodel_name="data_import_template",
        required=True,
        ondelete="cascade",
        help="Data Import Template this action rule belongs to.",
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
        help="Order the action rules are applied in.",
    )
    action_type = fields.Selection(
        string="Action Type",
        selection=[
            ("write", "Write Field"),
            ("o2m_upsert", "One2many Upsert"),
            ("m2m_set", "Many2many Set"),
            ("python", "Python Code"),
        ],
        required=True,
        default="write",
        help=(
            "How this rule is applied to the matched record:\n"
            "- Write Field: writes Value Code to Field Name.\n"
            "- One2many Upsert: creates or updates a line in Field "
            "Name, matched by Key Code, with Vals Code.\n"
            "- Many2many Set: adds/removes/replaces Field Name using "
            "M2m Mode and Value Code.\n"
            "- Python Code: runs Python Code directly."
        ),
    )
    target_path = fields.Char(
        string="Target Path",
        help=(
            "Dot-separated path, starting from the Template's Target "
            "Model, of the record this rule is ultimately applied to "
            "(e.g. 'partner_id' to act on the matched record's "
            "partner instead of the record itself). Free text rather "
            "than a field picker because it must be able to traverse "
            "relations that no single field record represents. Leave "
            "empty to act on the matched record directly."
        ),
    )
    field_name = fields.Char(
        string="Field Name",
        help="Technical name of the field written on the resolved "
        "Target Path (or on the matched record when Target Path is "
        "empty). Used by Write Field, One2many Upsert and Many2many "
        "Set.",
    )
    relation_field = fields.Char(
        string="Relation Field",
        help="Technical name of the field on the One2many/Many2many "
        "comodel used together with Key Code to find an existing line "
        "to update instead of creating a duplicate. Used by One2many "
        "Upsert.",
    )
    column = fields.Char(
        string="Column",
        help="Column name (or 0-based index when No Header Line is "
        "checked on the Template) read from the source file row.",
    )
    value_code = fields.Text(
        string="Value Code",
        help=(
            "Python expression that resolves to the value written by "
            "Write Field, or added/removed/replaced by Many2many Set. "
            "Available variables:\n"
            "  - env, document, time, datetime, dateutil, timezone, "
            "float_compare, b64encode, b64decode\n"
            "  - row: dict of the current file row, keyed by column\n"
            "  - value: raw value of Column in the current row"
        ),
    )
    key_code = fields.Text(
        string="Key Code",
        help=(
            "Python expression that resolves to the value used, "
            "together with Relation Field, to find an existing "
            "One2many line to update instead of creating a duplicate. "
            "Used by One2many Upsert. Same available variables as "
            "Value Code."
        ),
    )
    vals_code = fields.Text(
        string="Vals Code",
        help=(
            "Python expression that resolves to a dict of values "
            "written to the One2many line found (or created) by Key "
            "Code. Used by One2many Upsert. Same available variables "
            "as Value Code."
        ),
    )
    python_code = fields.Text(
        string="Python Code",
        help=(
            "Python statements run directly against the matched "
            "record. Used by Python Code. Available variables:\n"
            "  - env, document, time, datetime, dateutil, timezone, "
            "float_compare, b64encode, b64decode\n"
            "  - row: dict of the current file row, keyed by column"
        ),
    )
    m2m_mode = fields.Selection(
        string="M2m Mode",
        selection=[
            ("add", "Add"),
            ("remove", "Remove"),
            ("replace", "Replace"),
        ],
        default="add",
        help="How Value Code is applied to Field Name. Used by "
        "Many2many Set.",
    )
    skip_if_empty = fields.Boolean(
        string="Skip If Empty",
        default=True,
        help="If checked, this rule is not applied at all when Column "
        "is empty for the current row, instead of writing an empty "
        "value.",
    )

    @api.constrains("target_path", "template_id")
    def _check_target_path(self):
        """Reject a ``target_path`` that does not resolve on the target.

        Delegates to ``check_dotted_path``, walking every dot-separated
        segment of ``target_path`` against the Template's
        ``model_id.model`` fields. Skipped when ``target_path`` is
        empty (the rule acts on the matched record directly) or the
        Template has no Target Model yet.

        :raises ValidationError: when a segment of ``target_path`` does
            not exist on the resolved model
        """
        for rec in self:
            if not rec.target_path:
                continue
            if not rec.template_id or not rec.template_id.model_id:
                continue
            check_dotted_path(
                rec.env,
                rec.template_id.model_id.model,
                rec.target_path,
                "Target Path",
            )
