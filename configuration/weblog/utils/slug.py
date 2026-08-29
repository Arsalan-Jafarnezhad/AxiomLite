from django.utils.text import slugify


def unique_slug(
    model_class,
    value,
    slug_field="slug",
    exclude_pk=None,
):
    """
    Generate a unique slug for `model_class` from `value`.

    `model_class` must be the actual model *class* (e.g. `Article`), not an
    instance — a previous version of this function was called as
    `unique_slug(self, self.title)` from `Article.save()`, which passed the
    instance itself and blew up with `AttributeError: Manager isn't
    accessible via Article instances` the moment `model.objects` was
    touched. That meant creating any article without a manually-set slug
    crashed immediately.

    Pass `exclude_pk` when regenerating a slug for an existing row (e.g. on
    update) so the object doesn't collide with its own current slug.
    """

    base = slugify(value)
    slug = base
    number = 1

    queryset = model_class.objects.all()
    if exclude_pk is not None:
        queryset = queryset.exclude(pk=exclude_pk)

    while queryset.filter(**{slug_field: slug}).exists():
        number += 1
        slug = f"{base}-{number}"

    return slug
