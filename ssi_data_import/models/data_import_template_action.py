# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

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
        help="How Value Code is applied to Field Name. Used by " "Many2many Set.",
    )
    skip_if_empty = fields.Boolean(
        string="Skip If Empty",
        default=True,
        help="If checked, this rule is not applied at all when Column "
        "is empty for the current row, instead of writing an empty "
        "value.",
    )

    def _resolve_target_record(self, target):
        """Return the record ``target_path`` points to from ``target``.

        Pure ``getattr`` walk over each dot-separated segment of
        ``target_path`` -- it cannot subscript into a dict/JSON
        value. Returns ``target`` unchanged when ``target_path`` is
        empty.

        :param target: resolved Target Model record this rule
            ultimately acts on
        :return: resolved recordset
        """
        self.ensure_one()
        record = target
        if self.target_path:
            for segment in self.target_path.split("."):
                record = getattr(record, segment)
        return record

    def _resolve_before(self, target):
        """Return the value this rule would overwrite, for Preview.

        Only Write Field and Many2many Set act on a single named
        field, so only those two Action Types return a value here --
        One2many Upsert and Python Code return ``None`` since neither
        has one field to read a "before" value from.

        :param target: resolved Target Model record, or a falsy
            (empty) recordset when previewing an On No Match =
            Create row, which has no existing record to read from
        :return: current field value (JSON-safe), or ``None``
        """
        self.ensure_one()
        if self.action_type not in ("write", "m2m_set"):
            return None
        if not self.field_name or not target:
            return None
        record = self._resolve_target_record(target)
        if not record:
            return None
        return self._jsonify(getattr(record, self.field_name, None))

    def _resolve_after(self, row, target):
        """Return the value this rule would write, for Preview.

        Evaluates Value Code (Write Field, Many2many Set) or Vals
        Code (One2many Upsert) against ``row``. Python Code has no
        single deterministic value to preview and always returns
        ``None`` -- previewing it would mean running it, which
        Resolve must never do.

        :param row: dict of the current file row, keyed by Column
        :param target: resolved Target Model record, or a falsy
            (empty) recordset when previewing an On No Match =
            Create row
        :return: intended value (JSON-safe), or ``None``
        """
        self.ensure_one()
        if self.action_type == "python":
            return None
        if self.skip_if_empty and self.column and not row.get(self.column):
            return None
        if self.action_type == "o2m_upsert":
            value = self._eval_code(self.vals_code, row)
        else:
            value = self._eval_code(self.value_code, row)
        return self._jsonify(value)

    def _eval_code(self, code, row):
        """Evaluate a Value/Vals Code expression for ``row``.

        Called only while building Preview -- never while applying
        changes to the Target Model. Available variables: ``env``,
        ``document`` (the Template), ``time``, ``datetime``,
        ``dateutil``, ``timezone``, ``float_compare``, ``b64encode``,
        ``b64decode``, ``row`` and ``value`` (raw value of Column in
        ``row``).

        :param code: Python expression to evaluate, or empty
        :param row: dict of the current file row, keyed by Column
        :return: evaluated value, or ``None`` when ``code`` is empty
        """
        self.ensure_one()
        if not code:
            return None
        localdict = self.template_id._get_default_localdict()
        localdict.update({"row": row, "value": row.get(self.column)})
        return safe_eval(code, localdict, mode="eval", nocopy=True)

    def _jsonify(self, value):
        """Convert an ORM value into a JSON-serializable value.

        :param value: any field value read from, or evaluated
            against, a Target Model record
        :return: value safe to pass to ``json.dumps``
        """
        if isinstance(value, models.BaseModel):
            return value.ids
        if isinstance(value, (datetime.date, datetime.datetime)):
            return value.isoformat()
        return value

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
