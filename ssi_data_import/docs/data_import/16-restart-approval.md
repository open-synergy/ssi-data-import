# Restart Approval Process — Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** user in group `Data Import - Validator` (`data_import_validator_group`)\
> **Requires:** `04-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**, and the record currently has **no
  approval template assigned** — the approval process is stalled with no approver to act
  on it. The shipped policy grants this action only in that situation, so the button
  stays hidden on a document whose approval process is healthy.
- **Config:** An active `policy.template` (**Standard**) grants `restart_approval_ok`
  for state `confirm` to the actor's group.
- **Config:** An active `approval.template` (**Standard**) for this model matches this
  record, with group `Data Import - Validator` (`data_import_validator_group`)
  configured as approver, so a process can actually be rebuilt.
- **Access:** User is in group `Data Import - Validator`
  (`data_import_validator_group`).

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Open the record whose approval process is stalled.
3. Click the **Restart Approval Process** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status remains **Waiting for Approval**.
- The existing approval records and active approvers are discarded, and a new approval
  process is requested from the approval template that now matches the record.
- Once every level of the rebuilt process is approved, the document moves on to **Queue
  To Done** exactly as it would have (see `05-approve.md`).
