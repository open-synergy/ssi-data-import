# Restart Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** user in group `Data Import - Validator` (`data_import_validator_group`)\
> **State:** `cancel` | `reject` → `draft`\
> **Requires:** `10-cancel`

## Pre-Condition

- **Record:** Status is **Cancelled** or **Rejected**.
- **Config:** An active `policy.template` (**Standard**) grants `restart_ok` for those
  states to the actor's group.
- **Access:** User is in group `Data Import - Validator`
  (`data_import_validator_group`).

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Open the record to restart.
3. Click the **Restart** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status returns to **Draft**.
- All approval records are removed and the approval template reference is cleared. A
  later Confirm (see `04-confirm.md`) starts the approval process from the beginning.
- **Data lines are kept as they are, and nothing already written to the Target Model is
  undone.** Restart does not re-parse the file and does not re-resolve the lines. This
  is what makes Restart the second half of the fix for a **Stale** or **Error** line:
  back in Draft, **Resolve** becomes available again and re-evaluates every line that is
  not already Done or Ignored (see `01-create.md`).
