# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import ValidationError


def check_dotted_path(env, model_name, path, field_label):
    """Validate every dot-separated segment of a free-text field path.

    Walks ``path`` (e.g. ``"partner_id.category_id.name"``) against the
    fields of ``model_name``, following each relational segment into
    its ``comodel_name``. ``data_import_template.matcher.field_path``
    and ``data_import_template.action.target_path`` are free-text
    ``Char`` fields (not ``ir.model.fields`` Many2one) because they
    must be able to reach a field through a chain of relations that no
    single field record represents, so this is the only place their
    correctness can be checked.

    :param env: Odoo Environment used to resolve models by name
    :param model_name: technical name of the model the path starts
        from (usually the template's ``model_id.model``)
    :param path: dot-separated field path to validate
    :param field_label: human-readable field name used in the error
        message (e.g. ``"Field Path"``)
    :raises ValidationError: when a segment does not exist on the
        current model, or the path continues past a non-relational
        segment
    """
    current_model_name = model_name
    segments = path.split(".")
    last_index = len(segments) - 1
    for index, segment in enumerate(segments):
        current_model = env[current_model_name]
        if segment not in current_model._fields:
            raise ValidationError(
                _(
                    "%(field_label)s: segment '%(segment)s' does not "
                    "exist on model '%(model)s'."
                )
                % {
                    "field_label": field_label,
                    "segment": segment,
                    "model": current_model_name,
                }
            )
        field = current_model._fields[segment]
        if index == last_index:
            break
        if not field.relational:
            raise ValidationError(
                _(
                    "%(field_label)s: segment '%(segment)s' on model "
                    "'%(model)s' is not a relational field, so the path "
                    "cannot continue further."
                )
                % {
                    "field_label": field_label,
                    "segment": segment,
                    "model": current_model_name,
                }
            )
        current_model_name = field.comodel_name
