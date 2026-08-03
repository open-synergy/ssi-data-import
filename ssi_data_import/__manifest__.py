# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=C8101
{
    "name": "Data Import",
    "version": "14.0.1.4.0",
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
        "ssi_transaction_confirm_mixin",
        "ssi_transaction_queue_done_mixin",
        "ssi_transaction_queue_cancel_mixin",
        "ssi_source_document_mixin",
        "queue_job_batch",
        "ssi_web_widget_json",
        "base_automation",
    ],
    "data": [
        "security/ir_module_category_data.xml",
        "security/res_groups/data_import_template.xml",
        "security/res_groups/data_import.xml",
        "security/ir_model_access/data_import_template.xml",
        "security/ir_model_access/data_import.xml",
        "security/ir_rule/data_import.xml",
        "ir_sequence/data_import.xml",
        "sequence_template/data_import.xml",
        "approval_template/data_import.xml",
        "policy_template/data_import.xml",
        "data/ir_actions_server_data.xml",
        "data/base_automation_data.xml",
        "menu.xml",
        "views/data_import_template_views.xml",
        "views/data_import_views.xml",
        "views/assets.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["openpyxl", "xlrd"]},
}
