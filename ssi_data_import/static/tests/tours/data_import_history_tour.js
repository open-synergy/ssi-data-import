odoo.define("ssi_data_import.data_import_history_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/data_import/15-view-import-history.md
    //
    // Flow 1 ("Open the record") is satisfied by the URL start_tour() is
    // called with -- a direct res.partner form URL -- rather than a menu
    // click-through: which menu owns res.partner varies by optional addon
    // (e.g. Contacts) and is not itself what this tour proves, see the IK's
    // Menu: metadata and Pre-Condition instead.
    tour.register(
        "ssi_data_import_data_import_view_history",
        {
            test: true,
        },
        [
            {
                content: "The record is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 2 — Click the Action gear icon
            {
                content: "Open the Action menu",
                trigger: ".o_cp_action_menus button:contains(Action)",
            },

            // Flow 3 — Click Import History
            {
                // Action menu item adalah komponen Owl; target klik yang
                // benar adalah <a> di dalam .o_menu_item, dan cocokkan
                // LABEL PERSIS -- :contains(Import History) sebagai
                // substring juga cocok pada label lain yang mengandung
                // kata "Import" bila modul lain menambahkannya.
                content: "Click Import History",
                trigger: ".o_cp_action_menus .o_menu_item a",
                run: function () {
                    var $historyItem = $(".o_cp_action_menus .o_menu_item a").filter(
                        function () {
                            return $(this).text().trim() === "Import History";
                        }
                    );
                    $historyItem[0].click();
                },
            },

            // Post-Condition — the Data Import - Data list opens, filtered
            // to this record's Source Document
            {
                content: "Import History list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Import History)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
            {
                content: "The Data line for this record is visible",
                trigger: ".o_data_row",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );
});
