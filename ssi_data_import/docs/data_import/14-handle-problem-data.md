# Handle Problem Data Import Rows

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** user in group `Data Import - User` (`data_import_user_group`)\
> **Requires:** `05-approve`\
> **Inline Actions:** `action_open_edit_wizard` (Edit), `action_retry` (Retry), `action_open_ignore_wizard`
> (Ignore), `action_retry_all_problem_data` (Retry All), `action_open_ignore_all_wizard`
> (Ignore All)

This action does not itself transition the document's own Status -- it acts on
individual Data lines -- so no `State:` is declared above. It may still cause an
automatic Status change as a side effect: see Post-Condition.

## Pre-Condition

- **Record:** Status is **Queue To Done**.
- **Record:** At least one Data line is in a problem state -- **Draft**, **Error**, **No
  Match**, **Multiple Matches**, **Conflict**, or **Stale** (shown with a colored State
  badge on the **Import Data** tab).
- **Access:** User is in group `Data Import - User` (or a group implying it).

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Open the record whose status is **Queue To Done** and that has at least one problem
   Data line.
3. On the **Import Data** tab, locate a problem Data line by its **State** badge.
4. Click **Ignore** on that row.
5. In the dialog that appears, fill in **Reason** explaining why the line is skipped.
6. Click **Save** (`action_confirm`) in the dialog footer.

## Post-Condition

- The Data line's **State** becomes **Ignored** and its **Ignore Reason** field is set
  to the text typed in step 5.
- If this was the last remaining Draft, Matched, Error, or Stale line, the document
  automatically moves to **Done** -- see `09-finish.md`.

## Alternative Actions

The **Ignore** button (steps 4-6 above) is one of four ways to settle a problem row, all
available on the same **Import Data** tab and gated to the same set of row states:

- **Edit** opens a dialog to overwrite the row's raw JSON `data`. Saving it validates
  the text is a JSON object, then returns the row to **Draft** -- it does **not** run
  Resolve or Apply, so click **Retry** afterwards to re-process it.
- **Retry** resets the row to **Draft**, clears its Error Message, then re-runs Resolve
  and Apply for that row alone, synchronously (no queue job involved).
- **Retry All**, shown at the top of the **Import Data** tab only while the document is
  **Queue To Done**, runs **Retry** for every problem row at once.
- **Ignore All**, shown next to **Retry All** under the same condition, opens a dialog
  for a single shared **Reason** and ignores every problem row with it in one step.

A row already **Done** or **Ignored** rejects every one of these actions -- both are
terminal, and this module keeps no rollback.
