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

            // Gerbang penstabil (issue #11): the statusbar status widget
            // ("state" field) is wrapped by the same legacy
            // FieldWrapper.updateModifiersValue implicated in the CI
            // race ("TypeError: Cannot set properties of null (setting
            // 'props')"). Waiting for it to settle on Draft here proves
            // that widget has finished mounting/applying its modifiers
            // BEFORE the next step edits a field and triggers an
            // onchange-driven re-render across the whole form -- the
            // re-render is what raced against a still-mounting widget.
            {
                content:
                    "Statusbar widget has settled on Draft (safe to edit fields now)",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                extra_trigger: ".o_form_view.o_form_editable",
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

    // IK: docs/data_import/04-confirm.md
    //
    // Pre-Condition (a Draft document whose Template is "Tour Confirm
    // Template") is prepared in Python (setUpClass) -- Flow always opens
    // from the menu, per odoo-development-ui-test.
    tour.register(
        "ssi_data_import_data_import_confirm",
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

            // Flow 2 — Open the record to confirm
            {
                content: "Open the record",
                trigger:
                    ".o_data_row:contains(Tour Confirm Template) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Gerbang penstabil (issue #11): wait for the statusbar status
            // widget -- rendered through the same legacy
            // FieldWrapper.updateModifiersValue implicated in the CI race
            // ("Cannot set properties of null (setting 'props')") -- to
            // settle on Draft (this document's known Pre-Condition state)
            // BEFORE clicking Confirm. Confirm triggers a full-form
            // re-render; clicking before this widget finished
            // mounting/applying its modifiers is what raced.
            {
                content: "Statusbar widget has settled on Draft",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                extra_trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 3 — Click the Confirm button
            {
                content: "Click the Confirm button",
                trigger: ".o_statusbar_buttons button[name='action_confirm']",
                extra_trigger: ".o_form_view",
            },

            // Flow 4 — Click OK on the confirmation dialog
            {
                content: "Confirm the dialog",
                trigger: ".modal-footer button.btn-primary",
                in_modal: true,
            },

            // Post-Condition — status changes to Waiting for Approval
            {
                content: "Status is Waiting for Approval",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='confirm'].btn-primary",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );

    // IK: docs/data_import/05-approve.md
    //
    // Pre-Condition (a document already Waiting for Approval, Template
    // "Tour Approve Template") is prepared in Python (setUpClass) by
    // calling action_confirm() directly, same convention as
    // odoo-development-ui-test patterns.md §E. With zero Data lines
    // (no file uploaded, same reasoning as the create tour above), Apply
    // has nothing to enqueue, so the document reaches Done synchronously
    // in the same request as Approve -- there is no separate click.
    tour.register(
        "ssi_data_import_data_import_approve",
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

            // Flow 2 — Open the record to approve
            {
                content: "Open the record",
                trigger:
                    ".o_data_row:contains(Tour Approve Template) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Gerbang penstabil (issue #11): wait for the statusbar status
            // widget -- rendered through the same legacy
            // FieldWrapper.updateModifiersValue implicated in the CI race
            // ("Cannot set properties of null (setting 'props')") -- to
            // settle on Waiting for Approval (this document's known
            // Pre-Condition state, set via action_confirm() in
            // setUpClass) BEFORE clicking Approve. Approve triggers a
            // full-form re-render; clicking before this widget finished
            // mounting/applying its modifiers is what raced.
            {
                content: "Statusbar widget has settled on Waiting for Approval",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='confirm'].btn-primary",
                extra_trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 3 — Click the Approve button
            {
                content: "Click the Approve button",
                trigger: ".o_statusbar_buttons button[name='action_approve_approval']",
                extra_trigger: ".o_form_view",
            },

            // Flow 4 — Click OK on the confirmation dialog
            {
                content: "Confirm the dialog",
                trigger: ".modal-footer button.btn-primary",
                in_modal: true,
            },

            // Post-Condition — every approval level is fulfilled (only one
            // is configured), so status moves straight to Done: zero Data
            // lines means there is nothing for Apply to enqueue.
            {
                content: "Status is Done",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='done'].btn-primary",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );

    // IK: docs/data_import/10-cancel.md
    //
    // Pre-Condition (a Done document, Template "Tour Cancel Template", and
    // a global-use base.cancel_reason) is prepared in Python (setUpClass).
    tour.register(
        "ssi_data_import_data_import_cancel",
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

            // Flow 2 — Open the record to cancel
            {
                content: "Open the record",
                trigger:
                    ".o_data_row:contains(Tour Cancel Template) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Gerbang penstabil (issue #11): wait for the statusbar status
            // widget -- rendered through the same legacy
            // FieldWrapper.updateModifiersValue implicated in the CI race
            // ("Cannot set properties of null (setting 'props')") -- to
            // settle on Done (this document's known Pre-Condition state,
            // reached via action_confirm() + action_approve_approval() in
            // setUpClass) BEFORE clicking Cancel. Cancel triggers a
            // full-form re-render; clicking before this widget finished
            // mounting/applying its modifiers is what raced.
            {
                content: "Statusbar widget has settled on Done",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='done'].btn-primary",
                extra_trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 3 — Click the Cancel button (type="action": name is a
            // numeric window action id, so it must be targeted by label)
            {
                content: "Click the Cancel button",
                trigger: ".o_statusbar_buttons button:enabled:contains('Cancel')",
                extra_trigger: ".o_form_view",
            },

            // Flow 4 — In the wizard that appears, select the Cancellation
            // Reason
            {
                // 14.0: do NOT prefix an in-modal trigger with ".modal" --
                // $modal_displayed already scopes the search to it.
                content: "Wizard is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
            {
                content: "Select the cancellation reason",
                trigger:
                    ".o_field_radio[name='cancel_reason_id'] " +
                    ".o_radio_item:contains(Tour Cancel Reason) input",
            },

            // Flow 5 — Click Confirm
            {
                content: "Confirm the wizard",
                trigger: ".modal-footer button[name='action_confirm']",
            },

            // Flow 6 — Click OK on the confirmation dialog (the wizard's
            // own Confirm button carries confirm="Are you sure?", stacking
            // a second dialog on top of the wizard)
            {
                content: "Confirm the dialog",
                trigger: ".modal-footer button.btn-primary",
                in_modal: true,
            },

            // Post-Condition — status changes to Cancelled; the Done Data
            // line and the target record it wrote are not touched (not
            // observable from this tour -- see the Apply unit tests).
            {
                content: "Status is Cancelled",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='cancel'].btn-primary",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );
});
