# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDataImportTemplateDelimiter(YamlTransactionCase):
    """Test ``_get_delimiter_character`` return value for every choice."""

    def setUp(self):
        """Create one template per ``delimiter`` selection value."""
        super().setUp()
        self.partner_model = self.env.ref("base.model_res_partner")
        self.Template = self.env["data_import_template"]

    def _create_template(self, delimiter):
        """Create a template with the given ``delimiter`` value.

        :param delimiter: one of the ``delimiter`` Selection values
        :return: the created ``data_import_template`` record
        """
        return self.Template.create(
            {
                "name": "Delimiter Template",
                "code": "/",
                "model_id": self.partner_model.id,
                "delimiter": delimiter,
            }
        )

    def test_get_delimiter_character(self):
        """Check ``_get_delimiter_character`` for every ``delimiter``.

        P1/L-01: ``action: call`` in ``odoo-yaml-test`` discards the
        method's return value, so the mapping from Selection key to
        actual character can only be asserted from Python.
        """
        expected = {
            "comma": ",",
            "semicolon": ";",
            "tab": "\t",
            "pipe": "|",
            "space": " ",
        }
        for delimiter, character in expected.items():
            template = self._create_template(delimiter)
            self.assertEqual(
                template._get_delimiter_character(),
                character,
                "Unexpected delimiter character for '%s'" % delimiter,
            )
