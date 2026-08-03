# View Import History

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** *(none — reached from the Action menu of any record whose model is
> configured as a Data Import Template's Target Model, e.g. Contacts > Customers for*
> `res.partner`*)*\
> **Actor:** user in group `Data Import - User` (`data_import_user_group`)

This action is not opened from the Data Import module's own menu. It is a contextual
action -- registered automatically, alongside **Duplicate** and **Export**, on the
Action menu of every model configured as a Target Model by at least one active
`data_import_template` -- so it is not itself a step in this model's own lifecycle and
no `State:` is declared above.

## Pre-Condition

- **Config:** At least one active `data_import_template` targets the record's model
  (Target Model).
- **Access:** User is in group `Data Import - User` (or a group implying it).
- **Record:** The record being viewed already exists (saved) -- the Action menu is
  unavailable on an unsaved record.

## Flow

1. Open the record whose model is configured as a Data Import Template's Target Model
   (e.g. a Customer record, if a Template targets `res.partner`).
2. Click the **Action** gear icon (⚙) in the top-right corner of the form.
3. Click **Import History**.

## Post-Condition

- The **Data Import - Data** list opens, showing every `data_import.data` line whose
  Source Document points at this record -- across every Data Import document that has
  ever touched it, regardless of that document's own Status.
- Each line's **State**, **Preview**, and (if any) **Error Message** are visible
  straight from this list -- this is the only place in the UI to see that history from
  the record's own side, since a document's own **Import Data** tab
  (`01-create.md`) only shows the lines belonging to that one document.

## Alternative Actions

The same Action menu also carries **Start Import**, next to **Import History**, bound
to this model's **list** view instead of its form view. It opens a new `data_import`
document (`01-create.md`) with **Template** pre-filtered to Templates targeting this
model -- everything past that point is the same Create flow, there is no separate IK
for it.
