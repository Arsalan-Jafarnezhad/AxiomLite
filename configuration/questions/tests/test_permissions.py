from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from questions.models import Language, Question
from questions.constants import Difficulty, QuestionStatus

class PermissionTests(TestCase):
    def setUp(self):
        U=get_user_model()
        self.user=U.objects.create_user(email="u@example.com",password="x")
        self.author=U.objects.create_user(email="a@example.com",password="x")
        self.language=Language.objects.create(name="Python",slug="python",code="python")
    def test_draft_not_public(self):
        q=Question.objects.create(title="Draft",description="x",difficulty=Difficulty.EASY,language=self.language,created_by=self.author)
        self.client.login(email="u@example.com",password="x")
        self.assertEqual(self.client.get(reverse("questions:detail",args=[q.slug])).status_code,404)
