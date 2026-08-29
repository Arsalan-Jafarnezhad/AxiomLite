"""Small AJAX endpoints for reactions and bookmarks (toggle-on-click)."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from weblog.models import Article
from weblog.services.bookmarks import is_bookmarked, toggle_bookmark
from weblog.services.reactions import reaction_summary, toggle_reaction


class ReactionToggleView(LoginRequiredMixin, View):
    """POST /article/<slug>/react/  body: emoji=👍"""

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        emoji = request.POST.get("emoji", "")

        try:
            active, _reaction = toggle_reaction(article=article, user=request.user, emoji=emoji)
        except ValueError as exc:
            return JsonResponse({"success": False, "error": str(exc)}, status=400)

        return JsonResponse({"success": True, "active": active, "summary": reaction_summary(article)})


class BookmarkToggleView(LoginRequiredMixin, View):
    """POST /article/<slug>/bookmark/"""

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        bookmarked = toggle_bookmark(article=article, user=request.user)
        return JsonResponse({"success": True, "bookmarked": bookmarked})
