# Create Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** user in group `Data Import - User` (`data_import_user_group`)\
> **State:** `—` → `draft`\
> **Inline Actions:** `action_load_data` (Load Data)

## Pre-Condition

- **Access:** User is in group `Data Import - User` (or a group implying it).
- **Config:** An active `data_import_template` exists for the source file to be
  imported, with a Target Model and File Format matching that file.
- **Config:** An active `sequence.template` exists for `data_import` (already shipped
  by this module).

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Date**: defaults to today; change if needed.
   - **Template**: the Data Import Template whose recipe parses the file and
     determines its Target Model.
   - **Import File**: upload the source file. Its format must match the selected
     Template's **File Format**.
4. Click **Save**.
5. On the **Import Data** tab, click **Load Data** to parse Import File into Data
   lines. Load Data is only available while the document is Draft — it disappears
   once the document moves past Draft. It may be clicked again after re-uploading a
   different Import File: existing Data lines are replaced, not duplicated. One Data
   line is created for every row of the source file.

## Post-Condition

- A new record is created and appears in the Data Imports list.
- The document remains in state **Draft**.
- One Data line appears in the **Import Data** tab for every row of the source file,
  and the **# Data** counter reflects that count.
