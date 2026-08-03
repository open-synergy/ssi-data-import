# Finish Data Import

> **Module:** ssi_data_import\
> **Model:** `data_import`\
> **Menu:** Data Import > Transactions > Data Imports\
> **Actor:** — (triggered automatically, no user action)\
> **State:** `queue_done` → `done`\
> **Requires:** `05-approve`

This transition has no button — it is triggered automatically by this module's
`base.automation`, which watches the Done queue job batch and re-checks completion every
time it changes.

## Pre-Condition

- **Record:** Status is **Queue To Done**.
- **Record:** Every Data line has left state Draft, Matched, Error and Stale — i.e. each
  line is Done, Ignored, No Match, Multiple Matches or Conflict. A document with no Data
  line at all (nothing to apply) satisfies this immediately.

## Flow

1. Apply's queue job runs for every Data line that was Matched when Queue To Done was
   reached (see `05-approve.md`), writing each line's Preview to its Target Model record
   and moving it to Done, Error or Stale.
2. Once the Done queue job batch finishes, `base.automation` re-checks the Pre-Condition
   above.
3. If it holds, the document moves to Done automatically. If a line is still Error or
   Stale, the document stays at Queue To Done — there is no button to force it past
   this; see `10-cancel.md` and `01-create.md`'s Stale note to recover.

## Post-Condition

- Status changes to **Done**.
- Every Data line that was Matched has been written to its Target Model record (or moved
  to Error/Stale instead, in which case the document would not have reached Done).
