# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast
import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from .data_import_common import check_dotted_path

#: Default shown to the user when a new Action's Value Code/Key Code
#: is left empty -- a bare expression (eval mode), documenting the
#: variables available at both Resolve (Preview) and Apply time.
_CODE_DEFAULT_EVAL = (
    "# Available: env, document, row, value\n"
    "# Apply only: record, target, line\n"
    "value"
)
#: Default shown for a new Action's Vals Code -- same variables as
#: ``_CODE_DEFAULT_EVAL``, but must resolve to a dict.
_VALS_CODE_DEFAULT_EVAL = (
    "# Available: env, document, row, value\n"
    "# Apply only: record, target, line\n"
    "# Must resolve to a dict of values.\n"
    "{}"
)
#: Default shown for a new Action's Python Code -- exec mode
#: statements, run only at Apply time (never previewed).
_CODE_DEFAULT_EXEC = (
    "# Available: env, document, row, value, record, target, line, "
    "result\n"
    "# Statements run directly against 'record'/'target'.\n"
)


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

    #: Maps each eval-mode code field to the ``action_type`` values
    #: that actually evaluate it, used by ``_check_eval_code_syntax``.
    _EVAL_CODE_FIELDS = {
        "value_code": ("write", "m2m_set"),
        "key_code": ("o2m_upsert",),
        "vals_code": ("o2m_upsert",),
    }

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
        default=_CODE_DEFAULT_EVAL,
        help=(
            "Python expression that resolves to the value written by "
            "Write Field, or added/removed/replaced by Many2many Set. "
            "Evaluated identically at Resolve (Preview) and Apply "
            "time. Available variables:\n"
            "  - env, document, time, datetime, dateutil, timezone, "
            "float_compare, b64encode, b64decode\n"
            "  - row: dict of the current file row, keyed by column\n"
            "  - value: raw value of Column in the current row\n"
            "  - record, target, line: only set while Apply runs -- "
            "referencing them fails at Resolve (Preview) time"
        ),
    )
    key_code = fields.Text(
        string="Key Code",
        default=_CODE_DEFAULT_EVAL,
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
        default=_VALS_CODE_DEFAULT_EVAL,
        help=(
            "Python expression that resolves to a dict of values "
            "written to the One2many line found (or created) by Key "
            "Code. Used by One2many Upsert. Same available variables "
            "as Value Code."
        ),
    )
    python_code = fields.Text(
        string="Python Code",
        default=_CODE_DEFAULT_EXEC,
        help=(
            "Python statements run directly against the matched "
            "record. Used by Python Code, only run at Apply time -- "
            "never evaluated for Preview. Available variables:\n"
            "  - env, document, time, datetime, dateutil, timezone, "
            "float_compare, b64encode, b64decode\n"
            "  - row: dict of the current file row, keyed by column\n"
            "  - value: raw value of Column in the current row\n"
            "  - record: resolved Target Model record\n"
            "  - target: record resolved from Target Path\n"
            "  - line: the data_import.data line being applied\n"
            "  - result: available for consistency with other code "
            "fields, but not read back by Apply"
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

    def _eval_code(self, code, row, record=None, target=None, line=None):
        """Evaluate a Value/Key/Vals Code expression for ``row``.

        Called by Resolve while building Preview (``record``/
        ``target``/``line`` left at their default ``None``) and,
        with those three filled in, by Apply while writing to the
        Target Model -- so the exact same expression is evaluated
        the exact same way in both contexts, keeping Preview a
        faithful preview of what Apply will write. Available
        variables: ``env``, ``document`` (the Template), ``time``,
        ``datetime``, ``dateutil``, ``timezone``, ``float_compare``,
        ``b64encode``, ``b64decode``, ``row``, ``value`` (raw value
        of Column in ``row``), and -- only when called by Apply --
        ``record`` (matched/created Target Model record), ``target``
        (record resolved from Target Path) and ``line`` (the
        ``data_import.data`` line being applied).

        :param code: Python expression to evaluate, or empty
        :param row: dict of the current file row, keyed by Column
        :param record: resolved Target Model record, only set by
            Apply
        :param target: resolved Target Path record, only set by
            Apply
        :param line: ``data_import.data`` line being applied, only
            set by Apply
        :return: evaluated value, or ``None`` when ``code`` is empty
        """
        self.ensure_one()
        if not code:
            return None
        localdict = self.template_id._get_default_localdict()
        localdict.update({"row": row, "value": row.get(self.column)})
        if record is not None:
            localdict.update({"record": record, "target": target, "line": line})
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

    @api.constrains("value_code", "key_code", "vals_code", "action_type")
    def _check_eval_code_syntax(self):
        """Reject a Value/Key/Vals Code with invalid expression syntax.

        Only checked for the field(s) actually evaluated by this
        rule's ``action_type`` (e.g. Key Code only applies to
        One2many Upsert), and only while non-empty.

        :raises ValidationError: when the field's content does not
            parse as a single Python expression
        """
        for rec in self:
            for field_name, applicable_types in rec._EVAL_CODE_FIELDS.items():
                if rec.action_type not in applicable_types:
                    continue
                code = getattr(rec, field_name)
                if not code:
                    continue
                rec._check_code_syntax(code, field_name, "eval")

    @api.constrains("python_code", "action_type")
    def _check_python_code_syntax(self):
        """Reject a Python Code with invalid statement syntax.

        :raises ValidationError: when Python Code does not parse
        """
        for rec in self:
            if rec.action_type != "python" or not rec.python_code:
                continue
            rec._check_code_syntax(rec.python_code, "python_code", "exec")

    def _check_code_syntax(self, code, field_name, mode):
        """Validate that ``code`` parses under ``mode``.

        :param code: Python source to validate
        :param field_name: technical field name, used in the error
            message
        :param mode: ``"eval"`` for a single expression, ``"exec"``
            for statements
        :raises ValidationError: when ``code`` has a syntax error
        """
        self.ensure_one()
        try:
            ast.parse(code, mode=mode)
        except SyntaxError as error:
            message = "%s has invalid Python syntax: %s" % (field_name, error)
            raise ValidationError(_(message)) from error

    def _apply(self, row, record, line):
        """Apply this rule to ``record`` for ``line``, per ``action_type``.

        Called by ``data_import.data._apply_existing`` for every
        Action, in sequence order, inside a savepoint -- any
        exception raised here (including ``UserError`` from
        ``_apply_o2m_upsert``) propagates up to that savepoint and is
        turned into this line's state Error.

        :param row: dict of the current file row, keyed by Column
        :param record: resolved Target Model record (matched or
            newly created)
        :param line: the ``data_import.data`` line being applied
        :return: nothing
        """
        self.ensure_one()
        if self.skip_if_empty and self.column and not row.get(self.column):
            return
        target = self._resolve_target_record(record)
        if self.action_type == "write":
            self._apply_write(row, record, target, line)
        elif self.action_type == "o2m_upsert":
            self._apply_o2m_upsert(row, record, target, line)
        elif self.action_type == "m2m_set":
            self._apply_m2m_set(row, record, target, line)
        elif self.action_type == "python":
            self._apply_python(row, record, target, line)

    def _apply_write(self, row, record, target, line):
        """Apply this Write Field rule to ``target``.

        :param row: dict of the current file row, keyed by Column
        :param record: resolved Target Model record
        :param target: record resolved from Target Path (``record``
            itself when Target Path is empty)
        :param line: the ``data_import.data`` line being applied
        :return: nothing
        """
        self.ensure_one()
        value = self._eval_code(self.value_code, row, record, target, line)
        target.write({self.field_name: value})

    def _apply_o2m_upsert(self, row, record, target, line):
        """Apply this One2many Upsert rule to ``target``.

        Finds an existing line on ``target[self.field_name]`` whose
        Relation Field equals Key Code's value and writes Vals Code
        to it; creates a new line instead when none matches.

        :param row: dict of the current file row, keyed by Column
        :param record: resolved Target Model record
        :param target: record resolved from Target Path
        :param line: the ``data_import.data`` line being applied
        :raises UserError: when Key Code's value matches more than
            one existing line
        :return: nothing
        """
        self.ensure_one()
        key_value = self._eval_code(self.key_code, row, record, target, line)
        vals = self._eval_code(self.vals_code, row, record, target, line) or {}
        o2m = target[self.field_name]
        matches = o2m.filtered_domain([(self.relation_field, "=", key_value)])
        if len(matches) > 1:
            error_message = """
Context: Applying One2many Upsert action
Problem: Key Code matched %d existing lines on field '%s'
Solution: Adjust Key Code so it matches at most one line""" % (
                len(matches),
                self.field_name,
            )
            raise UserError(_(error_message))
        if matches:
            matches.write(vals)
        else:
            create_vals = dict(vals)
            create_vals[self.relation_field] = key_value
            target.write({self.field_name: [(0, 0, create_vals)]})

    def _apply_m2m_set(self, row, record, target, line):
        """Apply this Many2many Set rule to ``target``.

        :param row: dict of the current file row, keyed by Column
        :param record: resolved Target Model record
        :param target: record resolved from Target Path
        :param line: the ``data_import.data`` line being applied
        :return: nothing
        """
        self.ensure_one()
        value = self._eval_code(self.value_code, row, record, target, line)
        ids = value.ids if isinstance(value, models.BaseModel) else (value or [])
        command = {"add": 4, "remove": 3}.get(self.m2m_mode)
        if command:
            target.write({self.field_name: [(command, i) for i in ids]})
        else:
            target.write({self.field_name: [(6, 0, ids)]})

    def _apply_python(self, row, record, target, line):
        """Run Python Code (exec mode) directly against ``record``.

        Unlike Write Field/One2many Upsert/Many2many Set, Python
        Code is never evaluated while building Preview -- it only
        ever runs here, at Apply time.

        :param row: dict of the current file row, keyed by Column
        :param record: resolved Target Model record
        :param target: record resolved from Target Path
        :param line: the ``data_import.data`` line being applied
        :return: nothing
        """
        self.ensure_one()
        localdict = self.template_id._get_default_localdict()
        localdict.update(
            {
                "row": row,
                "value": row.get(self.column),
                "record": record,
                "target": target,
                "line": line,
                "result": None,
            }
        )
        safe_eval(self.python_code, localdict, mode="exec", nocopy=True)
