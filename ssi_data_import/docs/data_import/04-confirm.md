# Confirm Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** user in group `Data Import - User` (`data_import_user_group`)\
> **State:** `draft` → `confirm`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**.
- **Record:** No Data line is in state **Conflict** (Resolve runs again automatically
  right before Confirm's policy check, so a Conflict left over from a stale review is
  still caught here).
- **Config:** An active `policy.template` (**Standard**) for this model grants
  `confirm_ok` for state `draft` to the actor's group.
- **Config:** An active `approval.template` (**Standard**) for this model matches this
  record and has at least one approver level (group `Data Import - Validator`,
  `data_import_validator_group`).
- **Access:** User is in group `Data Import - User` (`data_import_user_group`).

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Open the record to confirm.
3. Click the **Confirm** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Waiting for Approval**.
- Approval records are created for each approver level defined by the **Standard**
  approval template.
