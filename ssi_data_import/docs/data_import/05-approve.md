# Approve Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** user registered as approver on the pending approval level, via the **Standard**
> approval template, group `Data Import - Validator` (`data_import_validator_group`)\
> **State:** `confirm` → `queue_done`\
> **Requires:** `04-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Config:** An active `policy.template` (**Standard**) grants `approve_ok` to the
  actor.
- **Access:** User is registered as an approver on the approval level that is currently
  pending.

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Open the record to approve.
3. Click the **Approve** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- If there are still pending approval levels, status remains **Waiting for Approval**
  and the next level becomes pending.
- If all approval levels are fulfilled, status automatically moves to **Queue To Done**
  — the transition is triggered internally right after the last approval, with no
  separate button click required — and Apply fans out one queue job per Data line in
  state Matched (see `09-finish.md`).
