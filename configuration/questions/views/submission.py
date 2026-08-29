from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from questions.forms.submission import SubmissionForm
from questions.models import Question
from questions.selectors.statistics import get_question_statistics
from questions.selectors.submissions import (
    submission_for_user,
    user_submissions,
)
from questions.services.markdown import render_question_markdown
from questions.services.submission import create_submission


class SubmitSolutionView(LoginRequiredMixin, View):
    template_name = "questions/detail.html"

    def get_question(self):
        question = get_object_or_404(
            Question.objects.published(),
            slug=self.kwargs["slug"],
        )

        if question.status == "archived":
            raise Http404

        return question

    def post(self, request, *args, **kwargs):
        question = self.get_question()
        form = SubmissionForm(request.POST)

        if form.is_valid():
            submission = create_submission(
                user=request.user,
                question=question,
                code=form.cleaned_data["code"],
            )

            return redirect(
                "questions:submission-detail",
                pk=submission.pk,
            )

        return render(
            request,
            self.template_name,
            {
                "question": question,
                "form": form,
                "description_html": render_question_markdown(
                    question.description,
                ),
                "statistics": get_question_statistics(question),
            },
            status=400,
        )


class SubmissionListView(LoginRequiredMixin, View):
    template_name = "questions/submissions/list.html"
    paginate_by = 25

    def get_queryset(self):
        return user_submissions(self.request.user)

    def get_context_data(self):
        page = Paginator(
            self.get_queryset(),
            self.paginate_by,
        ).get_page(
            self.request.GET.get("page"),
        )

        return {
            "submissions": page,
        }

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            self.get_context_data(),
        )


class SubmissionDetailView(LoginRequiredMixin, View):
    template_name = "questions/submissions/detail.html"

    def get_submission(self):
        submission = submission_for_user(
            self.kwargs["pk"],
            self.request.user,
        )

        if not submission:
            raise Http404

        return submission

    def get(self, request, *args, **kwargs):
        submission = self.get_submission()

        return render(
            request,
            self.template_name,
            {
                "submission": submission,
            },
        )