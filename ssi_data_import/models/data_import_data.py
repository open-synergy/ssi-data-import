# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DataImportData(models.Model):  # pylint: disable=too-few-public-methods
    """
    One line per row read from a ``data_import`` document's Import
    File, storing the raw row as JSON. ``mixin.source_document``
    provides a generic pointer to whatever Target Model record this
    line ends up matched with. Finding that record (Matched/No
    Match/Multiple Matches) and applying changes to it
    (Conflict/Stale/Error/Ignored/Done) are implemented by later
    modules; this model only owns the raw row and its eventual
    processing state.
    """

    _name = "data_import.data"
    _description = "Data Import - Data"
    _inherit = [
        "mixin.source_document",
    ]
    _order = "import_id, sequence"

    import_id = fields.Many2one(
        string="# Import",
        comodel_name="data_import",
        required=True,
        ondelete="cascade",
        help="The data_import document this line belongs to.",
    )
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
        help="Row sequence from the source file.",
    )
    data = fields.Text(
        string="Data",
        help=(
            "Raw row data read from Import File, stored as a JSON "
            "object keyed by column name (or 0-based column index "
            "when the Template's No Header Line is checked)."
        ),
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("matched", "Matched"),
            ("no_match", "No Match"),
            ("multi_match", "Multiple Matches"),
            ("conflict", "Conflict"),
            ("stale", "Stale"),
            ("error", "Error"),
            ("ignored", "Ignored"),
            ("done", "Done"),
        ],
        default="draft",
        readonly=True,
        copy=False,
        help=(
            "Processing state of this line. Only 'Draft' is produced "
            "by this module -- the remaining values are set by the "
            "matching, preview and apply features implemented by "
            "later modules."
        ),
    )
    error_message = fields.Text(
        string="Error Message",
        copy=False,
        help="Error details recorded when this line ends up in state Error.",
    )
    ignore_reason = fields.Text(
        string="Ignore Reason",
        copy=False,
        help="Reason recorded when this line is ignored instead of applied.",
    )
    queue_job_id = fields.Many2one(
        string="Queue Job",
        comodel_name="queue.job",
        copy=False,
        help="Queue job that processed this line, if any.",
    )
