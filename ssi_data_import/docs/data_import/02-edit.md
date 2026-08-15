# Edit Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** user in group `Data Import - User` (`data_import_user_group`)\
> **Requires:** `01-create`\
> **Inline Actions:** `action_load_data` (Load Data), `action_resolve` (Resolve)

## Pre-Condition

- **Record:** Status is **Draft**. **Date**, **Template** and **Import File** are
  read-only in every other state, and while the document is in the approval process any
  write is rejected with _"The operation is under approval process."_
- **Access:** User is in group `Data Import - User` (or a group implying it).

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Find and open the record to edit.
3. Change the fields as needed:
   - **Date**: date of this import document.
   - **Template**: the Data Import Template whose recipe parses the file and determines
     its Target Model.
   - **Import File**: the source file. Its format must match the selected Template's
     **File Format**.
4. On the **Import Data** tab, click **Load Data** to re-parse **Import File** into Data
   lines. This is the only way to refresh the lines — they are never re-read on Save.
   Existing Data lines are replaced, not appended to, so the button may be clicked again
   after every change. Skipping it after changing **Template** or re-uploading **Import
   File** leaves the previous run's Data lines in place, and Confirm would then queue
   rows that no longer match the file on the document.
5. Click **Resolve** to re-link each Data line to its Target Model record using the
   current Template's Matcher rules. Resolve is read-only — it never writes to the
   Target Model — and may be run any number of times; running it twice in a row leaves
   every line in the same state. Skipping it here is safe but not advisable: Resolve
   runs again automatically right before Confirm's policy check, so an unreviewed
   **Conflict** line surfaces only then, as a Confirm that fails.
6. Click **Save**.

## Post-Condition

- The record is updated with the new values and remains in state **Draft**.
- If **Load Data** was used, the **Import Data** tab holds one Data line per row of the
  current **Import File**, and the **# Data** counter reflects that count.
- If **Resolve** was used, each Data line's **State** and **Preview** reflect the
  current Template's Matcher rules.
