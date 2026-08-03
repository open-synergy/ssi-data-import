# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class DataImportTemplate(models.Model):
    """
    Represents a reusable recipe for importing a third-party file into
    records that already exist in an Odoo model. Stores how the source
    file must be parsed (format, encoding, delimiter, sheet selection),
    which model the rows target, the Matcher rules used to find the
    existing record a row corresponds to, and the Action rules applied
    to that record once found. Actually parsing a file and running the
    recipe (the ``data_import`` transactional model) is out of scope
    for this model.
    """

    _name = "data_import_template"
    _description = "Data Import Template"
    _inherit = [
        "mixin.master_data",
        "mixin.localdict",
    ]

    # --- File format ---

    file_format = fields.Selection(
        string="File Format",
        selection=[
            ("csv", "CSV / Delimited Text"),
            ("xlsx", "Excel (.xlsx)"),
            ("xls", "Excel (.xls)"),
        ],
        required=True,
        default="csv",
        help=(
            "Format of the source file to be imported.\n"
            "- CSV / Delimited Text: parsed using Encoding, Delimiter "
            "and Text Qualifier below.\n"
            "- Excel (.xlsx): parsed with openpyxl, worksheet chosen "
            "with Sheet Selector below.\n"
            "- Excel (.xls): parsed with xlrd, worksheet chosen with "
            "Sheet Selector below."
        ),
    )
    sheet_selector = fields.Selection(
        string="Sheet Selector",
        selection=[
            ("index", "Index"),
            ("name", "Name"),
        ],
        default="index",
        help=(
            "How to pick the worksheet when File Format is an Excel "
            "format. Index picks the 0-based worksheet position; Name "
            "picks the worksheet whose name matches Sheet Name below. "
            "Ignored for CSV / Delimited Text files."
        ),
    )
    sheet_name = fields.Char(
        string="Sheet Name",
        help=(
            "Name of the worksheet to read when Sheet Selector = Name. "
            "Ignored when Sheet Selector = Index or File Format = CSV."
        ),
    )
    file_encoding = fields.Selection(
        string="Encoding",
        selection=[
            ("utf-8", "UTF-8"),
            ("utf-8-sig", "UTF-8 (with BOM)"),
            ("utf-16", "UTF-16"),
            ("utf-16-sig", "UTF-16 (with BOM)"),
            ("windows-1252", "Western (Windows-1252)"),
            ("iso-8859-1", "Western (Latin-1 / ISO 8859-1)"),
        ],
        default="utf-8",
        help="Character encoding of the source file. Ignored for Excel " "formats.",
    )
    delimiter = fields.Selection(
        string="Delimiter",
        selection=[
            ("comma", "comma (,)"),
            ("semicolon", "semicolon (;)"),
            ("tab", "tab"),
            ("pipe", "pipe (|)"),
            ("space", "space"),
        ],
        default="comma",
        help="Field delimiter used in the source file. Ignored for " "Excel formats.",
    )
    quotechar = fields.Char(
        string="Text Qualifier",
        size=1,
        default='"',
        help="Character used to quote fields containing special "
        "characters. Ignored for Excel formats.",
    )
    no_header = fields.Boolean(
        string="No Header Line",
        default=False,
        help=(
            "Check if the file does not contain a header row. When "
            "checked, use the column index (0-based) instead of the "
            "column name in the Matcher and Action tabs below."
        ),
    )
    skip_empty_lines = fields.Boolean(
        string="Skip Empty Lines",
        default=True,
        help="Skip blank rows when parsing the file.",
    )
    date_format = fields.Char(
        string="Date Format",
        default="%Y-%m-%d",
        help=(
            "Python strftime() format used to turn a date/datetime "
            "cell read from the source file into text before it is "
            "stored as JSON (e.g. '%Y-%m-%d'). Only used for cells "
            "that are an actual date/datetime value (as read by "
            "openpyxl/xlrd); ignored for CSV files, whose cells are "
            "already plain text."
        ),
    )
    offset_row = fields.Integer(
        string="Row Offset",
        default=0,
        help="Number of rows to skip from the top before parsing starts.",
    )
    offset_column = fields.Integer(
        string="Column Offset",
        default=0,
        help="Number of columns to skip from the left before parsing " "starts.",
    )

    # --- Target ---

    model_id = fields.Many2one(
        string="Target Model",
        comodel_name="ir.model",
        required=True,
        ondelete="cascade",
        help="Odoo model that imported rows are matched and written " "against.",
    )
    model_name = fields.Char(
        string="Target Model Technical Name",
        related="model_id.model",
        store=True,
        index=True,
        help="Technical name of the Target Model, kept in sync for use "
        "in domains and the code fields below.",
    )
    on_no_match = fields.Selection(
        string="On No Match",
        selection=[
            ("error", "Error"),
            ("skip", "Skip Row"),
            ("create", "Create Record"),
        ],
        required=True,
        default="error",
        help=(
            "What to do with a row when no existing Target Model record "
            "satisfies the Matcher rules below: Error stops the import, "
            "Skip Row ignores the row, Create Record creates a new "
            "record using Create Values Code instead."
        ),
    )
    on_multi_match = fields.Selection(
        string="On Multiple Matches",
        selection=[
            ("error", "Error"),
            ("first", "Use First Match"),
            ("update_all", "Update All Matches"),
        ],
        required=True,
        default="error",
        help=(
            "What to do with a row when more than one existing Target "
            "Model record satisfies the Matcher rules below: Error "
            "stops the import, Use First Match applies the Action rules "
            "to the first match only, Update All Matches applies them "
            "to every match."
        ),
    )
    create_vals_code = fields.Text(
        string="Create Values Code",
        help=(
            "Python expression that resolves to a dict of values used "
            "to create a new Target Model record when On No Match = "
            "Create Record. Available variables:\n"
            "  - env, document, time, datetime, dateutil, timezone, "
            "float_compare, b64encode, b64decode\n"
            "  - row: dict of the current file row, keyed by column"
        ),
    )

    # --- Recipe lines ---

    matcher_ids = fields.One2many(
        string="Matchers",
        comodel_name="data_import_template.matcher",
        inverse_name="template_id",
        copy=True,
        help="Rules used to find the existing Target Model record a "
        "file row corresponds to.",
    )
    action_ids = fields.One2many(
        string="Actions",
        comodel_name="data_import_template.action",
        inverse_name="template_id",
        copy=True,
        help="Changes applied to the matched (or newly created) Target "
        "Model record.",
    )
    binding_action_ids = fields.Many2many(
        string="Binding Actions",
        comodel_name="ir.actions.act_window",
        relation="rel_data_import_template_binding_action",
        column1="template_id",
        column2="action_id",
        copy=False,
        readonly=True,
        help=(
            "Import History and Start Import contextual actions bound "
            "to Target Model's Action menu, shared by every active "
            "Template targeting the same Target Model. Kept in sync "
            "automatically on create/write/unlink of any Template; use "
            "Target Model's Resync Data Import Binding action (on "
            "Settings > Technical > Database Structure > Models) to "
            "repair it after manual interference (e.g. one of the two "
            "actions deleted by hand)."
        ),
    )

    # xmlid of the res.groups every Import History / Start Import
    # contextual action is restricted to -- without it, both entries
    # would show up in the Action menu of every user who can merely
    # see the Target Model, even though History exposes a change
    # audit trail and Start Import is a bulk-write entry point.
    _BINDING_GROUP_XMLID = "ssi_data_import.data_import_user_group"

    # One spec per contextual action registered for a Target Model.
    # "history" opens data_import.data (the audit trail itself, see
    # Keputusan Desain) filtered to this record; "start" opens a new
    # data_import document with Template pre-filtered to this model
    # via data_import.template_id's own context-aware domain.
    _BINDING_ACTION_SPECS = (
        {
            "key": "history",
            "name": "Import History",
            "res_model": "data_import.data",
            "view_mode": "tree,form",
            "binding_view_types": "form",
        },
        {
            "key": "start",
            "name": "Start Import",
            "res_model": "data_import",
            "view_mode": "form",
            "binding_view_types": "list",
        },
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Create Templates, then (re)sync their Target Model's binding.

        :param vals_list: list of value dicts, one per Template
        :return: recordset of the newly created Templates
        """
        records = super().create(vals_list)
        records._sync_model_binding_for_models(records.mapped("model_id"))
        return records

    def write(self, vals):
        """Write, then re-sync binding for any Target Model this affects.

        Only ``model_id`` and ``active`` can change which model(s)
        currently have an active Template targeting them -- every
        other field is irrelevant to the binding, so the resync is
        skipped unless one of the two is in ``vals``.

        :param vals: values to write
        :return: ``True``, as returned by the base ``write()``
        """
        needs_sync = "model_id" in vals or "active" in vals
        old_models = self.mapped("model_id") if needs_sync else self.env["ir.model"]
        result = super().write(vals)
        if needs_sync:
            new_models = self.mapped("model_id")
            self._sync_model_binding_for_models(old_models | new_models)
        return result

    def unlink(self):
        """Delete Templates, then re-sync binding for their Target Model.

        :return: ``True``, as returned by the base ``unlink()``
        """
        affected_models = self.mapped("model_id")
        result = super().unlink()
        if affected_models:
            self._sync_model_binding_for_models(affected_models)
        return result

    def _sync_model_binding_for_models(self, models):
        """(Re)synchronize the binding of every model in ``models``.

        :param models: ``ir.model`` recordset of Target Models whose
            Import History / Start Import binding may need to be
            created, removed, or repaired
        :return: nothing
        """
        template_model = self.sudo()
        for target_model in models.sudo():
            template_model._sync_model_binding_for_model(target_model)

    def _sync_model_binding_for_model(self, target_model):
        """(Re)synchronize the binding of a single Target Model.

        Creates a missing Import History / Start Import action while
        at least one active Template targets ``target_model``,
        removes both once none does, and (re)attaches every active
        Template targeting it to whichever actions currently exist --
        covering both routine drift (a new Template joining a model
        that already has the actions) and manual interference (one
        action deleted by hand, repaired by
        ``ir.model.action_resync_data_import_binding``).

        :param target_model: single ``ir.model`` record, already
            ``sudo()``
        :return: nothing
        """
        templates = self.search(
            [("model_id", "=", target_model.id), ("active", "=", True)]
        )
        action_model = self.env["ir.actions.act_window"]
        current_action_ids = []
        for spec in self._BINDING_ACTION_SPECS:
            existing = action_model.search(
                [
                    ("binding_model_id", "=", target_model.id),
                    ("res_model", "=", spec["res_model"]),
                    ("binding_type", "=", "action"),
                ],
                limit=1,
            )
            if templates and not existing:
                existing = action_model.create(
                    self._build_binding_action_vals(target_model, spec)
                )
            elif not templates and existing:
                existing.unlink()
                existing = action_model
            if existing:
                current_action_ids.append(existing.id)
        if templates and current_action_ids:
            binding_ops = [(4, action_id) for action_id in current_action_ids]
            templates.write({"binding_action_ids": binding_ops})

    def _build_binding_action_vals(self, target_model, spec):
        """Build the ``ir.actions.act_window`` create values for ``spec``.

        :param target_model: single ``ir.model`` record the action is
            bound to
        :param spec: one entry of ``_BINDING_ACTION_SPECS``
        :return: dict of values for ``ir.actions.act_window.create()``
        """
        group = self.env.ref(self._BINDING_GROUP_XMLID)
        vals = {
            "name": spec["name"],
            "res_model": spec["res_model"],
            "view_mode": spec["view_mode"],
            "binding_model_id": target_model.id,
            "binding_type": "action",
            "binding_view_types": spec["binding_view_types"],
            "groups_id": [(6, 0, [group.id])],
        }
        if spec["key"] == "history":
            # Filters data_import.data to the rows whose Source
            # Document points at the record this action was opened
            # from -- active_id is injected by the client the same
            # way it is for any window action opened from a form.
            vals["domain"] = (
                "[('source_document_model_id','=',%d),"
                "('source_document_res_id','=',active_id)]" % target_model.id
            )
        else:
            # Read by data_import.template_id's own domain= to
            # pre-filter Template choices to this Target Model --
            # see models/data_import.py.
            vals["context"] = "{'default_target_model_name': '%s'}" % (
                target_model.model
            )
        return vals

    @api.constrains("model_id")
    def _check_model_id(self):
        """Reject a Target Model that is transient or abstract.

        Transient models (wizards) and abstract models have no table
        of their own to match/write records against, so they can never
        be a valid import target.

        :raises ValidationError: when ``model_id`` refers to a
            transient or abstract model
        """
        for rec in self:
            if not rec.model_id:
                continue
            if rec.model_id.transient:
                raise ValidationError(
                    _(
                        "Target Model '%s' is a wizard (transient) "
                        "model and cannot be used as a data import "
                        "target."
                    )
                    % rec.model_id.model
                )
            target = rec.env[rec.model_id.model]
            if getattr(target, "_abstract", False):
                raise ValidationError(
                    _(
                        "Target Model '%s' is an abstract model and "
                        "cannot be used as a data import target."
                    )
                    % rec.model_id.model
                )

    def _eval_create_vals(self, row):
        """Evaluate Create Values Code for ``row``, without creating.

        Used by Resolve (On No Match = Create) to preview the record
        that would be created; the caller never calls ``.create()``
        with the result during Resolve, since Resolve must not write
        to the Target Model. Available variables: ``env``,
        ``document`` (this Template), ``time``, ``datetime``,
        ``dateutil``, ``timezone``, ``float_compare``, ``b64encode``,
        ``b64decode`` and ``row`` (dict of the current file row,
        keyed by Column).

        :param row: dict of the current file row, keyed by Column
        :return: dict of values a Target Model record would be
            created with, or an empty dict when Create Values Code is
            empty
        """
        self.ensure_one()
        if not self.create_vals_code:
            return {}
        localdict = self._get_default_localdict()
        localdict.update({"row": row})
        return safe_eval(self.create_vals_code, localdict, mode="eval", nocopy=True)

    def _get_delimiter_character(self):
        """Return the actual character configured by ``delimiter``.

        :return: single delimiter character, defaulting to comma when
            ``delimiter`` is unset or unrecognized
        """
        self.ensure_one()
        return {
            "comma": ",",
            "semicolon": ";",
            "tab": "\t",
            "pipe": "|",
            "space": " ",
        }.get(self.delimiter, ",")
