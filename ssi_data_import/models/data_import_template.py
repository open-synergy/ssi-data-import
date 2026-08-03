# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
