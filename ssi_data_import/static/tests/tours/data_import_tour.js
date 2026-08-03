odoo.define("ssi_data_import.data_import_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/data_import/01-create.md
    //
    // Import File is left empty in this tour: there is no DOM signal a
    // tour can use to attach a real file to a hidden <input type="file">
    // reliably across browsers, so uploading is out of scope here (see
    // odoo-development-ui-test skill, patterns.md §Q). Load Data is still
    // clicked -- with no file it safely no-ops (_load_data returns early)
    // -- so the tour proves the button is reachable and does not break the
    // form. Whether Load Data actually produces one Data line per source
    // row is unit-test territory instead (test_data_import_load_data.py,
    // P10/L-09..L-11: building an in-memory xlsx + base64 needs real
    // Python).
    tour.register(
        "ssi_data_import_data_import_create",
        {
            test: true,
            url: "/web",
        },
        [
            // Flow 1 — Open the Data Import > Transactions > Data Imports menu
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Data Import app",
                trigger:
                    '.o_app[data-menu-xmlid="ssi_data_import.menu_root_data_import"]',
            },
            {
                content: "Open the Transactions menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_data_import.menu_data_import_transaction"]',
            },
            {
                content: "Open the Data Imports menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_data_import.data_import_menu"]',
            },
            {
                // Gerbang: tunggu action TUJUAN benar-benar terpasang.
                content: "Data Imports list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Data Imports)",
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

            // Flow 3 — Fill in the required fields (Date keeps its default;
            // Import File is not uploaded -- see comment above)
            {
                content: "Select the Template",
                trigger: ".o_field_many2one[name='template_id'] input",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text Tour Import Template",
            },
            {
                content: "Pick Tour Import Template from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(Tour Import Template)",
                in_modal: false,
            },

            // Flow 4 — Click Save
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
                extra_trigger: ".o_field_many2one[name='template_id'] input",
            },
            {
                content: "Record is saved",
                trigger: ".o_form_view.o_form_readonly",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 5 — On the Import Data tab, click Load Data
            {
                content: "Open the Import Data tab",
                trigger: ".o_notebook .nav-link:contains(Import Data)",
            },
            {
                content: "Click Load Data",
                trigger: "button[name='action_load_data']:enabled",
                extra_trigger: ".o_form_view.o_form_readonly",
            },

            // Flow 6 — Click Resolve
            {
                content: "Click Resolve",
                trigger: "button[name='action_resolve']:enabled",
                extra_trigger: ".o_form_view.o_form_readonly",
            },

            // Gerbang: Resolved Date is only filled once action_resolve()
            // has actually run and written to the record -- unlike the
            // Load Data click above, this is a genuine post-click signal.
            {
                content: "Resolve completed (Resolved Date is filled)",
                trigger: ".o_field_widget[name='resolved_date']:not(:empty)",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Post-Condition — the document is unaffected by Load Data or
            // Resolve with no Import File uploaded (zero Data lines to
            // resolve): it stays in Draft.
            {
                content: "Status is still Draft",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );
});
