odoo.define("ssi_data_import.data_import_handle_problem_row_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/data_import/14-handle-problem-data.md
    //
    // Pre-Condition (a document already Queue To Done, Template "Tour Problem Row
    // Template", with one Data line stuck in state Error) is prepared in Python
    // (setUpClass), same convention as the other data_import tours.
    tour.register(
        "ssi_data_import_data_import_handle_problem_row",
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
                content: "Data Imports list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Data Imports)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 2 — Open the record whose status is Queue To Done and that has
            // a problem Data line
            {
                content: "Open the record",
                trigger:
                    ".o_data_row:contains(Tour Problem Row Template) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 3 — On the Import Data tab, locate the problem Data line
            {
                content: "Open the Import Data tab",
                trigger: ".o_notebook .nav-link:contains(Import Data)",
            },
            {
                content: "The problem row shows the Error badge",
                trigger:
                    ".o_field_widget[name='data_ids'] .o_data_row .o_field_widget[name='state']:contains(Error)",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 4 — Click Ignore on that row
            {
                content: "Click Ignore on the problem row",
                trigger:
                    ".o_field_widget[name='data_ids'] .o_data_row button[name='action_open_ignore_wizard']:enabled",
            },
            {
                // 14.0: do NOT prefix an in-modal trigger with ".modal" -- the
                // trigger is already searched for inside the modal.
                content: "Ignore wizard is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 5 — Fill in Reason
            {
                content: "Fill in the Reason",
                trigger: ".o_field_widget[name='reason'] textarea",
                run: "text Tour ignore reason",
            },

            // Flow 6 — Click Save
            {
                content: "Save the wizard",
                trigger: ".modal-footer button[name='action_confirm']",
            },

            // Post-Condition — the row's State becomes Ignored, verified through
            // the tree (tour never asserts field values, only what is visible)
            {
                content: "The row's State becomes Ignored",
                trigger:
                    ".o_field_widget[name='data_ids'] .o_data_row .o_field_widget[name='state']:contains(Ignored)",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );
});
