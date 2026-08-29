from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Max
from django.http import Http404
from django.shortcuts import render
from django.views import View

from questions.constants import Difficulty
from questions.models import Language, Question, Submission, Tag
from questions.selectors.questions import (
    annotate_user_status,
    published_questions,
    question_for_user,
    annotate_question_statistics,
    sort_questions,
)
from questions.selectors.statistics import get_question_statistics
from questions.services.markdown import render_question_markdown


class QuestionListView(View):
    template_name = "questions/list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = published_questions()

        query = self.request.GET.get("q", "").strip()
        difficulty = self.request.GET.get("difficulty")
        language = self.request.GET.get("language")
        tag = self.request.GET.get("tag")
        sort = self.request.GET.get("sort", "newest")

        if query:
            qs = qs.search(query)

        if difficulty:
            qs = qs.filter(difficulty=difficulty)

        if language:
            qs = qs.filter(language__slug=language)

        if tag:
            qs = qs.filter(tags__slug=tag)

        qs = annotate_question_statistics(qs)
        qs = sort_questions(qs, sort)
        qs = annotate_user_status(qs, self.request.user)

        return qs

    def get_context_data(self):
        query = self.request.GET.get("q", "").strip()
        sort = self.request.GET.get("sort", "newest")

        page = Paginator(
            self.get_queryset(),
            self.paginate_by,
        ).get_page(
            self.request.GET.get("page"),
        )

        return {
            "questions": page,
            "languages": Language.objects.filter(is_active=True),
            "tags": Tag.objects.all(),
            "query": query,
            "sort": sort,
            "question_difficulties": Difficulty.choices,
        }

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            self.get_context_data(),
        )


class QuestionDetailView(View):
    template_name = "questions/detail.html"

    def get_question(self):
        question = question_for_user(
            self.kwargs["slug"],
            self.request.user,
        )

        if not question:
            raise Http404

        return question

    def get_context_data(self, question):
        stats = get_question_statistics(question)

        best_score = None
        solved = False

        if self.request.user.is_authenticated:
            submissions = Submission.objects.filter(
                user=self.request.user,
                question=question,
            )

            best_score = submissions.aggregate(
                best=Max("final_score"),
            )["best"]

            solved = submissions.filter(
                final_score=100,
            ).exists()

        return {
            "question": question,
            "description_html": render_question_markdown(
                question.description,
            ),
            "statistics": stats,
            "best_score": best_score,
            "solved": solved,
        }

    def get(self, request, *args, **kwargs):
        question = self.get_question()

        return render(
            request,
            self.template_name,
            self.get_context_data(question),
        )
