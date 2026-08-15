# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import io
import json

import openpyxl
from odoo_yaml_test import YamlTransactionCase

from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDataImportLoadData(YamlTransactionCase):
    """Python-only scenarios for ``data_import.action_load_data``.

    P10/L-09..L-11: every scenario here needs an in-memory ``.xlsx``
    file built with ``openpyxl`` and base64-encoded, which is
    impossible to express as a single ``EVAL:`` expression (no
    ``import``, no ``str``/``bytes`` builtins available to the
    sandbox).
    """

    def setUp(self):
        """Create a Template targeting ``res.partner`` as ``.xlsx``."""
        super().setUp()
        self.partner_model = self.env.ref("base.model_res_partner")
        self.Template = self.env["data_import_template"]
        self.Document = self.env["data_import"]
        self.template = self.Template.create(
            {
                "name": "Load Data Template",
                "code": "/",
                "model_id": self.partner_model.id,
                "file_format": "xlsx",
            }
        )

    def _build_xlsx_base64(self, header, rows):
        """Build an in-memory ``.xlsx`` file and return it base64-encoded.

        :param header: list of header cell values, or ``None`` to skip
        :param rows: list of row (list of cell values)
        :return: base64-encoded bytes of the built ``.xlsx`` file
        """
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        if header is not None:
            sheet.append(header)
        for row in rows:
            sheet.append(row)
        buffer = io.BytesIO()
        workbook.save(buffer)
        return base64.b64encode(buffer.getvalue())

    def _create_document(self, file_b64):
        """Create a ``data_import`` document carrying ``file_b64``.

        :param file_b64: base64-encoded bytes of the file to upload
        :return: the created ``data_import`` record
        """
        return self.Document.create(
            {
                "template_id": self.template.id,
                "import_file": file_b64,
                "import_file_name": "import.xlsx",
            }
        )

    def test_load_data_normalizes_integer_valued_float(self):
        """Integer-valued float cells are stored without a decimal suffix.

        P10/L-09..L-11: the fixture is a virtual account number cell
        written as a Python ``float`` (mirroring how openpyxl reads a
        General-formatted whole number back from an ``.xlsx`` file),
        which cannot be built inside an ``EVAL:`` expression.
        """
        file_b64 = self._build_xlsx_base64(
            ["Name", "VA Number"],
            [["Toko Pintu Kelas", 9036926273120.0]],
        )
        document = self._create_document(file_b64)
        document.action_load_data()

        self.assertEqual(len(document.data_ids), 1)
        row = json.loads(document.data_ids.data)
        self.assertEqual(row["VA Number"], "9036926273120")

    def test_load_data_is_idempotent(self):
        """Calling Load Data twice does not duplicate Data lines.

        P10/L-09..L-11: same in-memory ``.xlsx``-building constraint as
        above.
        """
        file_b64 = self._build_xlsx_base64(
            ["Name", "VA Number"],
            [["Toko A", 111.0], ["Toko B", 222.0]],
        )
        document = self._create_document(file_b64)

        document.action_load_data()
        self.assertEqual(len(document.data_ids), 2)

        document.action_load_data()
        self.assertEqual(len(document.data_ids), 2)

    def test_load_data_corrupt_file_raises_user_error(self):
        """A corrupt file raises a structured ``UserError``, not a traceback.

        P10/L-09..L-11: constructing the malformed payload as bytes
        also needs real Python, not ``EVAL:``.
        """
        file_b64 = base64.b64encode(b"this is not a real xlsx file")
        document = self._create_document(file_b64)

        with self.assertRaises(UserError) as capture:
            document.action_load_data()
        self.assertIn("Context:", str(capture.exception))
