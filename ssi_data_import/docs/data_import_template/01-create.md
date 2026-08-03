# Create Data Import Template

> **Module:** ssi_data_import\
> **Model:** `data_import_template`\
> **Menu:** Data Import > Configuration > Data Import Templates\
> **Actor:** user in group `Data Import Template` (`data_import_template_group`)

## Pre-Condition

- **Access:** User is in group `Data Import Template`.

## Flow

1. Open the **Data Import > Configuration > Data Import Templates** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Name**: descriptive name of the template.
   - **Code**: unique code identifying the template.
   - **Target Model** (Target tab): the Odoo model imported rows are matched and written
     against.
4. On the **File Format** tab, review **File Format** and the fields below it (Encoding,
   Delimiter, Text Qualifier for CSV; Sheet Selector, Sheet Name for Excel) so they
   match the source file. The defaults are already correct for a comma-separated CSV
   file with a header row.
5. Click **Save**.

## Post-Condition

- A new record is created and appears in the Data Import Templates list.
