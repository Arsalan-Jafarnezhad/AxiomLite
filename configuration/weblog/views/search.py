from django.views.generic import ListView

from weblog.services.search import (
    advanced_search,
)


class SearchView(ListView):
    """
    Search published articles.
    """

    template_name = "weblog/search.html"

    context_object_name = "articles"

    paginate_by = 10

    def get_query(
        self,
    ):
        return self.request.GET.get(
            "q",
            "",
        ).strip()

    def get_queryset(
        self,
    ):

        query = self.get_query()

        return advanced_search(
            query=query,
            category=self.request.GET.get(
                "category",
            ),
            tag=self.request.GET.get(
                "tag",
            ),
            author=self.request.GET.get(
                "author",
            ),
            series=self.request.GET.get(
                "series",
            ),
            featured=self.get_boolean_filter(
                "featured",
            ),
            pinned=self.get_boolean_filter(
                "pinned",
            ),
            min_reading_time=self.request.GET.get(
                "min_reading_time",
            ),
            max_reading_time=self.request.GET.get(
                "max_reading_time",
            ),
        )

    def get_boolean_filter(
        self,
        key,
    ):
        """
        Convert query params into booleans.

        Examples:

            ?featured=true
            ?featured=false
        """

        value = self.request.GET.get(
            key,
        )

        if value is None:
            return None

        return value.lower() in (
            "true",
            "1",
            "yes",
        )

    def get_context_data(
        self,
        **kwargs,
    ):

        context = super().get_context_data(
            **kwargs,
        )

        context.update(
            query=self.get_query(),
            filters={
                "category": self.request.GET.get(
                    "category",
                ),
                "tag": self.request.GET.get(
                    "tag",
                ),
                "author": self.request.GET.get(
                    "author",
                ),
                "series": self.request.GET.get(
                    "series",
                ),
                "featured": self.request.GET.get(
                    "featured",
                ),
                "pinned": self.request.GET.get(
                    "pinned",
                ),
                "min_reading_time": self.request.GET.get(
                    "min_reading_time",
                ),
                "max_reading_time": self.request.GET.get(
                    "max_reading_time",
                ),
            },
        )

        return context
