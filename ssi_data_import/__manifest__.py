# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=C8101
{
    "name": "Data Import",
    "version": "14.0.1.1.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "contributors": [
        "Andhitia Rama <andhitia.r@gmail.com>",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "ssi_master_data_mixin",
        "ssi_localdict_mixin",
        "web_tour",
    ],
    "data": [
        "security/ir_module_category_data.xml",
        "security/res_groups/data_import_template.xml",
        "security/ir_model_access/data_import_template.xml",
        "menu.xml",
        "views/data_import_template_views.xml",
        "views/assets.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["openpyxl", "xlrd"]},
}
