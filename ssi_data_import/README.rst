.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========
Data Import
===========

Defines ``data_import_template``, a reusable recipe for importing a
third-party file (CSV/XLSX/XLS) into records that already exist in an
Odoo model: how the file is parsed, which model is targeted, the
Matcher rules used to find the existing record a row corresponds to,
and the Action rules applied once a match is found.

Also defines ``data_import``, the transactional document that uploads
an actual file, carries it through an approval workflow, and splits
it into ``data_import.data`` lines (one JSON row each) using its
Template's recipe.


Work Instruction
================

Data Import Template
--------------------

* `Create Data Import Template <docs/data_import_template/01-create.html>`_

Data Import
-----------

* `Create Data Import <docs/data_import/01-create.html>`_
* `Edit Data Import <docs/data_import/02-edit.html>`_
* `Delete Data Import <docs/data_import/03-delete.html>`_
* `Confirm Data Import <docs/data_import/04-confirm.html>`_
* `Approve Data Import <docs/data_import/05-approve.html>`_
* `Reject Data Import <docs/data_import/06-reject.html>`_
* `Finish Data Import <docs/data_import/09-finish.html>`_
* `Cancel Data Import <docs/data_import/10-cancel.html>`_
* `Restart Data Import <docs/data_import/12-restart.html>`_
* `Reset Document Number - Data Import <docs/data_import/13-reset-number.html>`_
* `Handle Problem Data Import Rows <docs/data_import/14-handle-problem-data.html>`_
* `View Import History <docs/data_import/15-view-import-history.html>`_
* `Restart Approval Process - Data Import <docs/data_import/16-restart-approval.html>`_
* `Reload Template Policy - Data Import <docs/data_import/17-reload-template-policy.html>`_


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/ssi-data-import
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list (Must be on developer mode)
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *Data Import*
6.  Install the module


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/open-synergy/ssi-data-import/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>

Maintainer
----------

.. image:: https://simetri-sinergi.id/logo.png
   :alt: PT. Simetri Sinergi Indonesia
   :target: https://simetri-sinergi.id

This module is maintained by the PT. Simetri Sinergi Indonesia.
