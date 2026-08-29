from django.conf import settings
from django.utils.timezone import now


def website_information(request):
    context = {}
    website_title = settings.WEBSITE_TITLE
    context["website_title"] = website_title
    return context
