from django import template

register = template.Library()


@register.filter
def model_fields(obj):
    """
    Returns a list of ``{"label": ..., "value": ...}`` dicts for every
    concrete field on *obj*, in declaration order.

    Used by ``generic_detail.html`` so a single template can render the
    detail page for any model without hand-writing a field list per model.
    Display-only helper properties (``*_display``, ``final_price`` etc.)
    are NOT included here — add them explicitly in a model-specific
    template block if you need them front and center.
    """
    rows = []
    for field in obj._meta.get_fields():
        if not getattr(field, "concrete", False):
            continue
        if field.many_to_many:
            continue
        try:
            value = getattr(obj, field.name)
        except Exception:
            continue
        # Prefer the human-readable choice label when available.
        display_getter = getattr(obj, f"get_{field.name}_display", None)
        if callable(display_getter):
            value = display_getter()
        rows.append({"label": field.verbose_name, "value": value})
    return rows


@register.filter
def getattribute(obj, name):
    return getattr(obj, name, "")
