odoo.define("ssi_data_import.data_import_template_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/data_import_template/01-create.md
    tour.register(
        "ssi_data_import_data_import_template_create",
        {
            test: true,
            url: "/web",
        },
        [
            // Flow 1 — Open the Data Import > Configuration >
            // Data Import Templates menu
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Data Import app",
                trigger:
                    '.o_app[data-menu-xmlid="ssi_data_import.menu_root_data_import"]',
            },
            {
                content: "Open the Configuration menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_data_import.menu_data_import_configuration"]',
            },
            {
                content: "Open the Data Import Templates menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_data_import.data_import_template_menu"]',
            },
            {
                // Gerbang: tunggu action TUJUAN benar-benar terpasang.
                content: "Data Import Templates list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Data Import Templates)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 2 — Click the New button
            {
                content: "Click Create",
                trigger: ".o_list_button_add",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open in edit mode",
                trigger: ".o_form_view.o_form_editable",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 3 — Fill in the required fields
            {
                content: "Fill in Name",
                trigger: ".o_field_widget[name='name']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text Tour Data Import Template",
            },
            {
                content: "Fill in Code",
                trigger: ".o_field_widget[name='code']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text /",
            },
            {
                content: "Open the Target tab",
                trigger: ".o_notebook .nav-link:contains(Target)",
            },
            {
                content: "Select the Target Model",
                trigger: ".o_field_many2one[name='model_id'] input",
                run: "text Contact",
            },
            {
                // Exact-text match: the autocomplete also lists unrelated
                // models whose description merely CONTAINS "Contact" (e.g.
                // "Qweb Field Contact"), which a plain :contains() selector
                // would also match.
                content: "Pick Contact from the dropdown",
                trigger: ".ui-autocomplete .ui-menu-item a",
                in_modal: false,
                run: function () {
                    var $option = $(".ui-autocomplete .ui-menu-item a").filter(
                        function () {
                            return $(this).text().trim() === "Contact";
                        }
                    );
                    $option[0].click();
                },
            },

            // Flow 4 — Open the File Format tab and review it
            {
                content: "Open the File Format tab",
                trigger: ".o_notebook .nav-link:contains(File Format)",
            },
            {
                content: "File Format tab is displayed",
                trigger: ".o_field_widget[name='file_format']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 5 — Click the Save button
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
            },
            {
                content: "Record is saved",
                trigger: ".o_form_view.o_form_readonly",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Post-Condition — the new record appears in the list
            {
                content: "Back to the Data Import Templates list",
                trigger:
                    ".breadcrumb-item.o_back_button a:contains(Data Import Templates)",
            },
            {
                content: "The new record is visible in the list",
                trigger: ".o_data_row:contains(Tour Data Import Template)",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );
});
