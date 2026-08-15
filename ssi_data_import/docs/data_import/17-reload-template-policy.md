# Reload Template Policy — Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** administrator in group `Settings / Technical Settings` (`base.group_system`)\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** None — usable regardless of status.
- **Config:** At least one active `policy.template` exists for this model (the
  **Standard** template is shipped by this module), so a matching template can be found.
- **Access:** User is in group `Settings / Technical Settings` (`base.group_system`).
  The **Policies** tab that contains this button is only visible to this group.

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Open the record whose assigned policy template should be re-evaluated.
3. On the **Policies** tab, click **Reload Template Policy**.

## Post-Condition

- **Policy Template** is recomputed and re-assigned to the highest-sequence
  `policy.template` for this model whose condition currently matches the record.
- This may change which action buttons are granted — `confirm_ok`, `approve_ok`,
  `reject_ok`, `restart_approval_ok`, `queue_cancel_ok`, `cancel_ok`, `restart_ok`,
  `done_ok`, `queue_done_ok`, `manual_number_ok` — without changing the record's status
  and without touching its Data lines.
