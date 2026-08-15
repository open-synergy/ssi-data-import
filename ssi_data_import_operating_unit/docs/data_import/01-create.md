# Create Data Import

> **Module:** ssi_data_import_operating_unit
>
> **Extends:** ssi_data_import — model `data_import`, aksi `01-create`

## Additional Pre-Condition

- **Config:** Group `operating_unit.group_multi_operating_unit` is active — the
  **Operating Unit** field described below is only visible when this group is enabled.

## Additional Fields

When this module is installed, the create form gains one optional field:

- **Operating Unit**: The operating unit that owns this data import document.
  Automatically filled from the current user's default operating unit
  (`res.users.operating_unit_default_get()`). Change if needed. Visible only when group
  `operating_unit.group_multi_operating_unit` is active. On the create form it renders
  directly (subject to that group). In the **tree** view it is additionally hidden by
  default (`optional="hide"`) — show it via the list column picker.

## Modified — Record Visibility

- The Data Imports list is filtered by operating unit (record rule
  `data_import_rule_ou`). A user in group `data_import_ou_group` only sees data import
  documents whose **Operating Unit** is one of the operating units assigned to them.
  This is not a Flow step.
