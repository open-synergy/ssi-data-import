# Reset Document Number — Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** user in group `Data Import - Validator` (`data_import_validator_group`)\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**.
- **Config:** An active `policy.template` (**Standard**) grants `manual_number_ok` for
  state `draft` to the actor's group.
- **Config:** An active `sequence.template` exists for `data_import` (already shipped by
  this module).
- **Access:** User is in group `Data Import - Validator`
  (`data_import_validator_group`).

## Flow

1. Open the **Data Import > Transactions > Data Imports** menu.
2. Open the record whose document number will be reset.
3. Click the **Reset Document Number** button (or edit the **# Document** field directly
   and change it to **/**).
4. Click **OK** on the confirmation dialog (only when the button was used).

## Post-Condition

- Document number returns to **/**.
- The record will receive an automatic number when it reaches **Queue To Done**, not on
  Confirm — this model creates its sequence at that state.
- With the number back at **/**, the Draft document becomes deletable again (see
  `03-delete.md`).
