# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiDataImport(HttpSavepointCase):
    """Tour tests for the ``data_import`` work instructions."""

    @classmethod
    def setUpClass(cls):
        """Grant the user group and prepare the Template the tour picks.

        Import File is intentionally never uploaded by the tour -- see
        the comment in ``data_import_tour.js`` -- so whether Load Data
        actually produces Data lines from a real file is covered by
        ``test_data_import_load_data.py`` instead.
        """
        super().setUpClass()
        # Pre-Condition: the Data Imports menu is gated by the user
        # group. Without it the tour dies on its first step -- the
        # menu is never rendered.
        cls.env.ref("ssi_data_import.data_import_user_group").sudo().write(
            {"users": [(4, cls.env.ref("base.user_admin").id)]}
        )
        cls.env["data_import_template"].sudo().create(
            {
                "name": "Tour Import Template",
                "code": "/",
                "model_id": cls.env.ref("base.model_res_partner").id,
            }
        )

    def test_create(self):
        """Run the create tour for ``data_import``.

        IK: docs/data_import/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_data_import_data_import_create",
            login="admin",
        )
