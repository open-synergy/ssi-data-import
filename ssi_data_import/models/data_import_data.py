# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import json

from odoo import _, fields, models
from odoo.exceptions import UserError


class DataImportData(models.Model):
    """
    One line per row read from a ``data_import`` document's Import
    File, storing the raw row as JSON. ``mixin.source_document``
    provides a generic pointer to whatever Target Model record this
    line ends up matched with. Resolve (``data_import.action_resolve``)
    is the read-only, repeatable phase that finds that record using
    the Template's Matcher rules, fills ``preview``/``value_hash``,
    and flags conflicting lines (Conflict/Ignored are set by Resolve
    or its conflict checks). Apply (``_apply``, run from the queue
    job fanned out by ``data_import._10_enqueue_data_apply_jobs`` on
    Queue Done) writes each Matched line's Preview to the Target
    Model -- gated by a staleness check against ``value_hash`` (state
    Stale on mismatch) and wrapped in a savepoint so a failure never
    leaves a partial write (state Error) nor stops the batch.

    A line stuck in a problem state (Draft, Error, No Match, Multiple
    Matches, Conflict or Stale) is never a dead end: ``action_retry``
    re-runs Resolve/Apply for it alone, ``action_open_edit_wizard``
    opens a dialog to fix its raw Data, and ``action_open_ignore_wizard``
    records a Reason and skips it for good. Done and Ignored lines are
    both terminal -- this module keeps no rollback, so neither is
    ever reopened.
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
    preview = fields.Text(
        string="Preview",
        copy=False,
        help=(
            "JSON object, filled by Resolve, mapping each configured "
            "Action's key to its {'before', 'after'} value pair. "
            "Permanent audit trail -- never cleared once this line "
            "reaches Done, since this module writes changes without "
            "keeping a rollback snapshot."
        ),
    )
    value_hash = fields.Char(
        string="Value Hash",
        copy=False,
        help=(
            "SHA-256 fingerprint of every 'before' value in Preview, "
            "sorted by Preview key. Recomputed on every Resolve; "
            "meant to be re-checked when this line is applied, to "
            "detect that the Target Model record changed since."
        ),
    )
    conflict_data_id = fields.Many2one(
        string="Conflicting Line",
        comodel_name="data_import.data",
        readonly=True,
        copy=False,
        help=(
            "Other Data line -- in the same document -- that resolved "
            "to the same Target Model record first. Filled by Resolve "
            "when this line's state becomes Conflict."
        ),
    )

    _resolvable_states = (
        "draft",
        "no_match",
        "multi_match",
        "conflict",
        "stale",
        "error",
    )

    def init(self):
        """Ensure a composite index on the Source Document pointer.

        Speeds up the Import History contextual action registered per
        Target Model by ``data_import_template`` (see
        ``_build_binding_action_vals``), whose domain filters on
        exactly ``(source_document_model_id, source_document_res_id)``
        together. Without this index, opening History on any record
        scans the whole ``data_import.data`` table as it grows.

        :return: nothing
        """
        super().init()
        self._cr.execute(
            "SELECT indexname FROM pg_indexes WHERE indexname = %s",
            ("data_import_data_source_document_idx",),
        )
        if not self._cr.fetchone():
            self._cr.execute(
                "CREATE INDEX data_import_data_source_document_idx "
                "ON data_import_data "
                "(source_document_model_id, source_document_res_id)"
            )

    def _resolve(self, template):
        """Read-only (re-)resolution of this line against ``template``.

        Builds the search domain from ``template.matcher_ids``,
        searches the Target Model, and applies On No Match / On
        Multiple Matches. Never writes to the Target Model -- only
        this line's own ``state``, ``source_document_*``, ``preview``
        and ``value_hash`` are written. Idempotent: calling it again
        with the same ``data``/Template reaches the same state.

        :param template: the ``data_import_template`` in use
        :return: nothing
        """
        self.ensure_one()
        row = json.loads(self.data or "{}")
        domain = self._build_matcher_domain(template, row)
        if domain is None:
            self._set_error(_("A Required matcher's Column is empty for this row."))
            return

        target_model = self.env[template.model_name]
        matches = target_model.search(domain)

        if not matches:
            self._resolve_no_match(template, row)
        elif len(matches) > 1:
            self._resolve_multi_match(template, row, matches)
        else:
            self._resolve_matched(template, row, matches)

    def _build_matcher_domain(self, template, row):
        """Build the AND-combined search domain for this row.

        Combines every ``template.matcher_ids`` line, in Matcher
        ``sequence`` order, into one domain. A Required matcher whose
        Column is empty in ``row`` aborts the whole domain instead of
        searching with an empty value.

        :param template: the ``data_import_template`` in use
        :param row: dict of the current file row, keyed by Column
        :return: list of ``(field_path, operator, value)`` domain
            leaves, or ``None`` when a Required matcher's Column is
            empty in ``row``
        """
        self.ensure_one()
        domain = []
        for matcher in template.matcher_ids:
            raw_value = row.get(matcher.column)
            if matcher.required and not raw_value:
                return None
            domain.append(
                (
                    matcher.field_path,
                    matcher.operator,
                    matcher._resolve_value(row),
                )
            )
        return domain

    def _resolve_no_match(self, template, row):
        """Apply Template's On No Match to a row with zero matches.

        :param template: the ``data_import_template`` in use
        :param row: dict of the current file row, keyed by Column
        :return: nothing
        """
        self.ensure_one()
        if template.on_no_match == "skip":
            self.write(
                {
                    "state": "ignored",
                    "ignore_reason": _(
                        "No matching record found; Template is "
                        "configured to skip rows with no match."
                    ),
                    "error_message": False,
                }
            )
        elif template.on_no_match == "create":
            self._resolve_create(template, row)
        else:
            self.write({"state": "no_match", "error_message": False})

    def _resolve_multi_match(self, template, row, matches):
        """Apply Template's On Multiple Matches to a multi-match row.

        "Use First Match" and "Update All Matches" both preview
        against the first match here -- applying every match for
        "Update All Matches" is implemented by the later Apply
        module, which is expected to re-run the Matcher search itself
        rather than rely on this line's single ``source_document_*``
        pointer.

        :param template: the ``data_import_template`` in use
        :param row: dict of the current file row, keyed by Column
        :param matches: recordset of every Target Model record found
        :return: nothing
        """
        self.ensure_one()
        if template.on_multi_match in ("first", "update_all"):
            self._resolve_matched(template, row, matches[0])
        else:
            self.write({"state": "multi_match", "error_message": False})

    def _resolve_matched(self, template, row, target):
        """Mark this line Matched against a single ``target`` record.

        :param template: the ``data_import_template`` in use
        :param row: dict of the current file row, keyed by Column
        :param target: the single resolved Target Model record
        :return: nothing
        """
        self.ensure_one()
        preview = self._build_preview(template, row, target)
        self.write(
            {
                "state": "matched",
                "source_document_model_id": template.model_id.id,
                "source_document_res_id": target.id,
                "preview": json.dumps(preview, default=str),
                "value_hash": self._compute_value_hash(preview),
                "error_message": False,
            }
        )

    def _resolve_create(self, template, row):
        """Preview the record On No Match = Create would create.

        Evaluates ``template.create_vals_code`` and stores the result
        under a ``"create"`` key in Preview -- it is never actually
        called here, since Resolve must not write to the Target
        Model. ``source_document_res_id`` is left at ``0``: there is
        no existing record yet, only a prepared set of values.

        :param template: the ``data_import_template`` in use
        :param row: dict of the current file row, keyed by Column
        :return: nothing
        """
        self.ensure_one()
        create_vals = template._eval_create_vals(row)
        preview = {"create": {"before": None, "after": create_vals}}
        self.write(
            {
                "state": "matched",
                "source_document_model_id": template.model_id.id,
                "source_document_res_id": 0,
                "preview": json.dumps(preview, default=str),
                "value_hash": self._compute_value_hash(preview),
                "error_message": False,
            }
        )

    def _build_preview(self, template, row, target):
        """Build the before/after preview dict for ``target``.

        :param template: the ``data_import_template`` in use
        :param row: dict of the current file row, keyed by Column
        :param target: the resolved Target Model record
        :return: dict mapping each Action's key (its Field Name, or
            ``"action_<sequence>"`` when Field Name is empty) to
            ``{"before": ..., "after": ...}``
        """
        self.ensure_one()
        preview = {}
        for action in template.action_ids.sorted("sequence"):
            key = action.field_name or ("action_%s" % action.sequence)
            preview[key] = {
                "before": action._resolve_before(target),
                "after": action._resolve_after(row, target),
            }
        return preview

    def _compute_value_hash(self, preview):
        """Fingerprint every 'before' value of ``preview``.

        :param preview: dict built by ``_build_preview`` or
            ``_resolve_create``
        :return: hex SHA-256 digest of every ``before`` value, sorted
            by Preview key for a deterministic result
        """
        before_values = [preview[key]["before"] for key in sorted(preview)]
        payload = json.dumps(before_values, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _set_error(self, message):
        """Mark this line Error with ``message``.

        :param message: human-readable explanation stored in
            ``error_message``
        :return: nothing
        """
        self.ensure_one()
        self.write({"state": "error", "error_message": message})

    def _check_cross_document_conflict(self):
        """Warn when another document already applied to this target.

        Called by ``data_import._check_resolve_conflicts`` once per
        distinct target within a document, after intra-document
        duplicates are already flagged Conflict. Never changes
        ``state`` -- the other document's Done line is not this
        document's business to invalidate, only to warn about.

        :return: nothing
        """
        self.ensure_one()
        other = self.search(
            [
                ("id", "!=", self.id),
                ("import_id", "!=", self.import_id.id),
                ("state", "=", "done"),
                (
                    "source_document_model_id",
                    "=",
                    self.source_document_model_id.id,
                ),
                ("source_document_res_id", "=", self.source_document_res_id),
            ],
            limit=1,
        )
        if not other:
            return
        warning = _(
            "Target record was already updated by a Done line on "
            "another document (%s)."
        ) % (other.import_id.name or other.import_id.id)
        self.error_message = (
            "%s\n%s" % (self.error_message, warning) if self.error_message else warning
        )

    # -------------------------------------------------------------------
    # Apply -- queue job entry point (data_import._10_enqueue_data_apply)
    # -------------------------------------------------------------------

    def _apply(self):
        """Apply this line's Preview to the Target Model.

        Entry point of the per-line queue job created by
        ``data_import._10_enqueue_data_apply_jobs``. Wrapped in a
        database savepoint and never raises: any exception from
        ``_apply_action`` (including one raised by an Action's
        ``_apply``) is caught here and stored as state Error, so the
        enclosing queue job always reaches state Done -- letting the
        batch (and this document's auto-completion) proceed even
        when this line failed.

        :return: nothing
        """
        self.ensure_one()
        try:
            with self.env.cr.savepoint():
                self._apply_action()
        except Exception as error:  # pylint: disable=broad-except
            self.write({"state": "error", "error_message": str(error)})

    def _apply_action(self):
        """Apply this line, gated by a staleness check on existing targets.

        Called inside ``_apply``'s savepoint. A line with no existing
        Target Model record yet (``source_document_res_id`` is ``0``
        -- Resolve matched it by Template's On No Match = Create
        Record) always applies: there is nothing it could have gone
        stale against. A line with an existing target recomputes a
        fresh Preview against it and compares the fingerprint of its
        ``before`` values (the same computation Resolve itself used)
        against the stored ``value_hash``; a mismatch means the
        target changed since Resolve, so this line moves to state
        Stale and nothing is written.

        :return: nothing
        """
        self.ensure_one()
        template = self.import_id.template_id
        row = json.loads(self.data or "{}")
        if not self.source_document_res_id:
            self._apply_create(template, row)
            return
        record = self.env[template.model_name].browse(self.source_document_res_id)
        if not record.exists():
            self.write(
                {
                    "state": "stale",
                    "error_message": _(
                        "Target record no longer exists; re-run Resolve " "to continue."
                    ),
                }
            )
            return
        current_preview = self._build_preview(template, row, record)
        current_hash = self._compute_value_hash(current_preview)
        if current_hash != self.value_hash:
            self.write(
                {
                    "state": "stale",
                    "error_message": _(
                        "Target record changed since Resolve; re-run "
                        "Resolve to continue."
                    ),
                }
            )
            return
        for action in template.action_ids.sorted("sequence"):
            action._apply(row, record, self)
        self.write({"state": "done", "error_message": False})

    def _apply_create(self, template, row):
        """Create the Target Model record for an On No Match = Create line.

        Mirrors ``data_import_template._eval_create_vals``, the same
        method Resolve used to preview this line's ``"create"`` key
        -- there is no staleness check here since, before this call,
        the record did not exist yet.

        :param template: the ``data_import_template`` in use
        :param row: dict of the current file row, keyed by Column
        :return: nothing
        """
        self.ensure_one()
        create_vals = template._eval_create_vals(row)
        new_record = self.env[template.model_name].create(create_vals)
        self.write(
            {
                "state": "done",
                "source_document_res_id": new_record.id,
                "error_message": False,
            }
        )

    # -------------------------------------------------------------------
    # Edit JSON, Ignore, and Retry -- opened from the row itself
    # -------------------------------------------------------------------

    def _check_actionable_state(self):
        """Ensure this line can still be edited, ignored, or retried.

        :raises UserError: when ``state`` is not one of
            ``_resolvable_states`` -- Done and Ignored are both
            terminal, and this module never reverts a change once
            applied, so allowing Edit/Ignore/Retry there would
            silently pretend to fix a line whose Target Model write
            already happened (Done) or that was already skipped on
            purpose (Ignored)
        """
        self.ensure_one()
        if self.state not in self._resolvable_states:
            error_message = """
Context: Handling a problem Data line
Database ID: %s
Problem: Line is in state '%s' and cannot be edited, ignored, or retried
Solution: Only Draft, Error, No Match, Multi Match, Conflict, Stale lines qualify
""" % (
                self.id,
                self.state,
            )
            raise UserError(_(error_message))

    def _check_json_object(self, raw):
        """Validate ``raw`` parses to a JSON object (a dict).

        :param raw: text typed by the user in the Edit JSON wizard
        :raises UserError: when ``raw`` is not valid JSON, or parses
            to something other than a JSON object (e.g. a list or a
            scalar)
        :return: the parsed ``dict``
        """
        self.ensure_one()
        try:
            parsed = json.loads(raw or "")
        except (TypeError, ValueError) as error:
            error_message = """
Context: Editing a Data line's raw JSON
Database ID: %s
Problem: The text is not valid JSON
Solution: Fix the JSON syntax and try again
""" % (
                self.id,
            )
            raise UserError(_(error_message)) from error
        if not isinstance(parsed, dict):
            error_message = """
Context: Editing a Data line's raw JSON
Database ID: %s
Problem: The JSON must be an object (e.g. {"field": "value"}), not %s
Solution: Wrap the value in a JSON object keyed by column name
""" % (
                self.id,
                type(parsed).__name__,
            )
            raise UserError(_(error_message))
        return parsed

    def _edit_json(self, raw):
        """Overwrite this line's raw Data and return it to Draft.

        Called by the ``edit_data_import_row`` wizard's Confirm.
        Never runs Resolve or Apply itself -- the user is expected to
        click Retry afterwards to re-process the corrected row.

        :param raw: JSON text typed by the user, validated to be a
            JSON object by ``_check_json_object``
        :return: nothing
        """
        self.ensure_one()
        self._check_actionable_state()
        parsed = self._check_json_object(raw)
        self.write(
            {
                "data": json.dumps(parsed),
                "state": "draft",
                "error_message": False,
            }
        )

    def _check_ignore_reason(self, reason):
        """Validate ``reason`` is filled before ignoring a line.

        :param reason: text typed by the user in the Ignore wizard
        :raises UserError: when ``reason`` is empty -- Ignore is a
            terminal, unrecoverable outcome (this module keeps no
            rollback), so skipping the reason would erase the only
            audit trail the feature leaves behind
        """
        if not (reason or "").strip():
            error_message = """
Context: Ignoring a Data line
Problem: Reason is empty
Solution: Explain why this line is being ignored before confirming
"""
            raise UserError(_(error_message))

    def _ignore(self, reason):
        """Mark this line Ignored with ``reason``.

        Called by both the ``ignore_data_import_row`` wizard
        (single line) and ``data_import._ignore_all_problem_data``
        (bulk, one shared Reason). Since this settles the line
        outside the queue's own Apply path, its orphaned queue job
        (if any) is force-completed and the document is re-checked
        for Done right after.

        :param reason: text stored on ``ignore_reason``, already
            validated non-empty by ``_check_ignore_reason``
        :return: nothing
        """
        self.ensure_one()
        self._check_actionable_state()
        self._check_ignore_reason(reason)
        self.write({"state": "ignored", "ignore_reason": reason})
        self._finalize_terminal_state()
        self.import_id._reevaluate_completion()

    def _finalize_terminal_state(self):
        """Force-complete this line's orphaned queue job, if any.

        Safety net for Ignore and Retry: this line just left the
        queue's own control (its outcome was decided by a direct
        write or by a synchronous Retry, not by the queue job fanned
        out for it), so a queue job still sitting in a non-terminal
        state would otherwise leave the document's Done batch
        (``done_queue_job_batch_id``) stuck forever, and the document
        would never reach Done.

        :return: nothing
        """
        self.ensure_one()
        job = self.queue_job_id
        if job and job.state not in ("done", "failed", "cancelled"):
            job.button_done()

    def _retry(self):
        """Reset this line to Draft, then re-run Resolve and Apply.

        Unlike the queue-driven Apply started by
        ``data_import._10_enqueue_data_apply_jobs``, this runs
        synchronously and only for this single line -- meant for a
        user fixing one problem line at a time, not for the initial
        mass Apply.

        :return: nothing
        """
        self.ensure_one()
        self._check_actionable_state()
        self.write({"state": "draft", "error_message": False})
        self._resolve(self.import_id.template_id)
        if self.state == "matched":
            self._apply()
        if self.state in ("done", "ignored"):
            self._finalize_terminal_state()
        self.import_id._reevaluate_completion()

    def action_open_edit_wizard(self):
        """Open the Edit JSON wizard for this line.

        :return: an ``ir.actions.act_window`` dict
        """
        for record in self.sudo():
            result = record._open_edit_wizard()
        return result

    def _open_edit_wizard(self):
        """Build the window action opening the Edit JSON wizard.

        :return: an ``ir.actions.act_window`` dict, ``target`` "new",
            pointing at ``edit_data_import_row``
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Edit Data"),
            "res_model": "edit_data_import_row",
            "view_mode": "form",
            "target": "new",
        }

    def action_open_ignore_wizard(self):
        """Open the Ignore wizard for this line.

        :return: an ``ir.actions.act_window`` dict
        """
        for record in self.sudo():
            result = record._open_ignore_wizard()
        return result

    def _open_ignore_wizard(self):
        """Build the window action opening the Ignore wizard.

        :return: an ``ir.actions.act_window`` dict, ``target`` "new",
            pointing at ``ignore_data_import_row``
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Ignore Data Line"),
            "res_model": "ignore_data_import_row",
            "view_mode": "form",
            "target": "new",
        }

    def action_retry(self):
        """Reset this line to Draft and re-run Resolve/Apply for it.

        :return: nothing
        """
        for record in self.sudo():
            record._retry()
