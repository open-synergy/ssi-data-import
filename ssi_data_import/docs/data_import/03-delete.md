# Delete Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** user in group `Data Import - User` (`data_import_user_group`)\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**. Deletion is refused in every other state.
- **Record:** Document number is still **/** (not yet generated). A document only
  receives its number when it reaches **Queue To Done**, so this holds by default — but
  not if the number was set by hand (see `13-reset-number.md`).
- **Access:** User is in group `Data Import - User` (or a group implying it).

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Select one or more records to delete (check the checkbox).
3. Click **Action** > **Delete**.
4. Click **OK** to confirm.

## Post-Condition

- The selected records are permanently removed from the system, together with their Data
  lines.
- Nothing is undone on the Target Model. Deleting a document that never left Draft is
  safe because Apply only ever runs from **Queue To Done** — but a document that did
  reach Queue To Done or Done must be **cancelled**, not deleted, and even then the rows
  it already wrote stay written (see `10-cancel.md`).
- The **Import File** hash is released, so the same file may be uploaded again by a new
  document.
