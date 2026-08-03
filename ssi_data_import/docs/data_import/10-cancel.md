# Cancel Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** user in group `Data Import - Validator` (`data_import_validator_group`)\
> **State:** `draft` | `confirm` | `queue_done` | `done` → `cancel`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**, **Waiting for Approval**, **Queue To Done**, or
  **Done**.
- **Access:** User is in group `Data Import - Validator`
  (`data_import_validator_group`).

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Open the record to cancel.
3. Click the **Cancel** button.
4. In the wizard that appears, select the **Cancellation Reason**.
5. Click **Confirm**.
6. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Cancelled**.
- **No Data line is touched, and no Target Model record is touched.** Cancel only
  changes this document's own status field — this is deliberate, not a limitation: a
  Data line already Done keeps whatever it wrote, permanently, even after Cancel. See
  the warning banner shown on this document while it is Queue To Done or Done, and
  `01-create.md`'s Stale note for how to actually fix a bad row (Cancel, then Restart,
  then Resolve again).
