from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from questions.constants import Difficulty, QuestionStatus, SubmissionStatus
from questions.forms.submission import SubmissionForm
from questions.models import Language, Question, Submission
from questions.utils import clamp_score, compare_outputs, normalize_output
from questions.widgets import QuestionMarkdownWidget


class QuestionUtilityTests(TestCase):
    def test_output_normalization_modes_and_numeric_comparison(self):
        self.assertEqual(normalize_output([" A ", "B"], "trimmed"), "A \nB")
        self.assertEqual(normalize_output(["A B"], "case_insensitive"), "a b")
        self.assertEqual(normalize_output(["A B"], "whitespace_insensitive"), "AB")
        self.assertTrue(compare_outputs(["1.0"], ["1"], "numeric"))
        self.assertFalse(compare_outputs(["x"], ["1"], "numeric"))
        self.assertEqual(clamp_score("150"), 100)
        self.assertEqual(clamp_score("-1"), 0)

    def test_submission_form_and_widget_context(self):
        form = SubmissionForm(data={"code": "print(1)"})
        self.assertTrue(form.is_valid(), form.errors)
        widget = QuestionMarkdownWidget()
        context = widget.get_context("description", "hello", {})
        self.assertEqual(context["widget"]["attrs"]["rows"], 28)
        self.assertIn("upload_url", context)
        self.assertIn("styles/weblog/markdown-editor.css", widget.media._css["all"])


class SubmissionViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("submitter@example.com", "password123")
        self.other = get_user_model().objects.create_user("other@example.com", "password123")
        self.language = Language.objects.create(name="Python", slug="python", code="python")
        self.question = Question.objects.create(
            title="Published task", description="# Solve", difficulty=Difficulty.EASY,
            language=self.language, created_by=self.user, status=QuestionStatus.PUBLISHED,
        )

    def test_submit_requires_authentication_and_invalid_form_is_400(self):
        submit_url = reverse("questions:submit", args=[self.question.slug])
        response = self.client.post(submit_url, {"code": "print(1)"})
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user)
        response = self.client.post(submit_url, {"code": ""})
        self.assertEqual(response.status_code, 400)

    def test_valid_submission_redirects_and_detail_is_private_to_owner(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("questions:submit", args=[self.question.slug]), {"code": "print(1)"})
        self.assertEqual(response.status_code, 302)
        submission = Submission.objects.get(user=self.user, question=self.question)
        self.assertRedirects(response, reverse("questions:submission-detail", args=[submission.pk]))
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("questions:submission-detail", args=[submission.pk])).status_code, 404)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("questions:submission-list")).status_code, 200)
