from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from weblog.services.image_upload import save_article_image


class ArticleImageUploadView(
    LoginRequiredMixin,
    View,
):

    def post(self, request, *args, **kwargs):

        image = request.FILES.get("image")

        if not image:
            return JsonResponse(
                {
                    "error": "No image provided."
                },
                status=400,
            )

        if not image.content_type.startswith(
            "image/"
        ):
            return JsonResponse(
                {
                    "error": "File must be an image."
                },
                status=400,
            )

        if image.size > 10 * 1024 * 1024:
            return JsonResponse(
                {
                    "error": "Image is too large."
                },
                status=400,
            )

        url = save_article_image(image)

        return JsonResponse(
            {
                "url": url,
            }
        )