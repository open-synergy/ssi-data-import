# Create Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** user in group `Data Import - User` (`data_import_user_group`)\
> **State:** `—` → `draft`\
> **Inline Actions:** `action_load_data` (Load Data), `action_resolve` (Resolve)

## Pre-Condition

- **Access:** User is in group `Data Import - User` (or a group implying it).
- **Config:** An active `data_import_template` exists for the source file to be
  imported, with a Target Model and File Format matching that file.
- **Config:** An active `sequence.template` exists for `data_import` (already shipped by
  this module).

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Date**: defaults to today; change if needed.
   - **Template**: the Data Import Template whose recipe parses the file and determines
     its Target Model.
   - **Import File**: upload the source file. Its format must match the selected
     Template's **File Format**.
4. Click **Save**.
5. On the **Import Data** tab, click **Load Data** to parse Import File into Data lines.
   Load Data is only available while the document is Draft — it disappears once the
   document moves past Draft. It may be clicked again after re-uploading a different
   Import File: existing Data lines are replaced, not duplicated. One Data line is
   created for every row of the source file.
6. Click **Resolve** to link each Data line to the Target Model record it corresponds
   to, using the Template's Matcher rules. Resolve is read-only — it never writes to the
   Target Model — and may be run again any number of times; running it twice in a row
   leaves every line in the same state. Review the **State** badge of each Data line
   before confirming the document:
   - **Matched** (default badge): a Target Model record was found (or, for a Template
     configured to create missing records, prepared to be created).
   - **No Match** / **Multiple Matches** (yellow): no record, or more than one record,
     satisfied the Template's Matcher rules. These do **not** block Confirm.
   - **Conflict** (red): this line and another line in the same document resolved to the
     same Target Model record — see the **Conflicting Line** field. **Confirm is blocked
     while any line is Conflict.**
   - **Error** (red): a Required matcher's Column was empty for this row, or the row
     found no Target Model record and the Template is configured to error. Resolve also
     runs automatically right before Confirm, so reviewing it here is optional but
     recommended — Confirm still fails on any Conflict line left unresolved.
   - **Stale** (red): only appears after Queue To Done, on a line whose Target Model
     record was changed by someone else after its Preview was built — Apply detects this
     and refuses to overwrite the newer value. A Stale line is never produced by Resolve
     itself. To fix it: **Cancel** the document (see `10-cancel.md`), **Restart** it
     back to Draft, then run **Resolve** again — it re-evaluates every Stale (and Error)
     line from scratch, leaving lines already Done untouched. While still Queue To Done,
     Edit, Retry, and Ignore on the row itself are a more direct alternative — see
     `14-handle-problem-data.md`.

## Post-Condition

- A new record is created and appears in the Data Imports list.
- The document remains in state **Draft**.
- One Data line appears in the **Import Data** tab for every row of the source file, and
  the **# Data** counter reflects that count.
- After Resolve, each Data line's **State** reflects whether its Target Model record was
  found, and Matched lines carry a **Preview** of the changes that would be applied.
