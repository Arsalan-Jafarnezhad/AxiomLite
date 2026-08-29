from django_filters import rest_framework as filters

from weblog.models import Article



class ArticleFilter(
    filters.FilterSet
):

    category = filters.CharFilter(
        field_name="category__slug"
    )


    author = filters.CharFilter(
        field_name="author__username"
    )


    tag = filters.CharFilter(
        field_name="tags__slug"
    )


    min_reading_time = filters.NumberFilter(
        field_name="reading_minutes",
        lookup_expr="gte"
    )


    max_reading_time = filters.NumberFilter(
        field_name="reading_minutes",
        lookup_expr="lte"
    )


    class Meta:

        model = Article

        fields = [
            "category",
            "author",
            "tag",
        ]