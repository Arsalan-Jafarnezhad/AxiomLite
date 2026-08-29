from django.contrib.auth import get_user_model
from django.test import TestCase
from questions.constants import Difficulty
from questions.models import Language, Question

class QuestionModelTests(TestCase):
    def test_slug_is_generated(self):
        u=get_user_model().objects.create_user(email="a@example.com",password="x")
        l=Language.objects.create(name="Python",slug="python",code="python")
        q=Question.objects.create(title="Hello World",description="# hi",difficulty=Difficulty.EASY,language=l,created_by=u)
        self.assertEqual(q.slug,"hello-world")
