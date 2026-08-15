# Reject Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** user registered as approver on the pending approval level, via the **Standard**
> approval template, group `Data Import - Validator` (`data_import_validator_group`)\
> **State:** `confirm` → `reject`\
> **Requires:** `04-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Config:** An active `policy.template` (**Standard**) grants `reject_ok` for state
  `confirm` to the actor — the shipped template grants it to whoever is an active
  approver on the record, not to a group.
- **Access:** User is registered as an approver on the approval level that is currently
  pending. The **Standard** approval template validates levels in sequence, so only the
  first unapproved level is pending.

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Open the record to reject.
3. Click the **Reject** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Rejected**.
- No queue job is created and no Data line is touched — Apply only ever fans out on the
  way to **Queue To Done** (see `05-approve.md`), which a rejected document never
  reaches. Nothing is written to the Target Model.
- The document can be brought back to **Draft** with **Restart** (see `12-restart.md`).
