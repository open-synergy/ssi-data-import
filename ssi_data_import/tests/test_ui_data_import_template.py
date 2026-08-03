# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestUiDataImportTemplate(HttpCase):
    """Tour tests for the ``data_import_template`` work instructions."""

    @classmethod
    def setUpClass(cls):
        """Grant the configurator group the create tour's menu requires."""
        super().setUpClass()
        # Pre-Condition: the Data Import Templates menu is gated by the
        # configurator group. Without it the tour dies on its first
        # step -- the menu is never rendered.
        cls.env.ref("ssi_data_import.data_import_template_group").sudo().write(
            {"users": [(4, cls.env.ref("base.user_admin").id)]}
        )

    def test_create(self):
        """Run the create tour for ``data_import_template``.

        IK: docs/data_import_template/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_data_import_data_import_template_create",
            login="admin",
        )
