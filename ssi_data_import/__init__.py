# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.api import SUPERUSER_ID, Environment

from . import models  # noqa: F401
from . import wizards  # noqa: F401


def uninstall_hook(cr, registry):
    """Remove every Import History / Start Import contextual action.

    These ``ir.actions.act_window`` records are created at runtime by
    ``data_import_template._sync_model_binding_for_model`` and never
    get an ``ir.model.data`` entry, so the normal module-uninstall
    cleanup (which only removes records owned via XML ID) never sees
    them -- they would otherwise be left dangling, bound to a Target
    Model that no longer has this module installed.

    :param cr: database cursor for the uninstalling transaction
    :param registry: registry of the uninstalling database
    :return: nothing
    """
    env = Environment(cr, SUPERUSER_ID, {})
    actions = env["ir.actions.act_window"].search(
        [
            ("res_model", "in", ("data_import", "data_import.data")),
            ("binding_model_id", "!=", False),
        ]
    )
    actions.unlink()
