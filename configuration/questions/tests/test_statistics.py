from django.test import TestCase
from django.contrib.auth import get_user_model
from questions.models import Language, Question, Submission
from questions.constants import SubmissionStatus, Difficulty
from questions.selectors.statistics import get_question_statistics

class StatisticsTests(TestCase):
    def setUp(self):
        self.User=get_user_model()
        self.language=Language.objects.create(name="Python",slug="python",code="python")
        self.question=Question.objects.create(title="Sum",description="# Sum",difficulty=Difficulty.EASY,language=self.language,created_by=self.User.objects.create_user(email="author@example.com",password="x"))
    def test_unique_users(self):
        users=[self.User.objects.create_user(email=f"u{i}@example.com",password="x") for i in range(3)]
        for i,u in enumerate(users):
            for score in ([100,50] if i==0 else ([100] if i==1 else [70,80])):
                Submission.objects.create(user=u,question=self.question,language=self.language,code="x",status=SubmissionStatus.COMPLETED,final_score=score)
        s=get_question_statistics(self.question)
        self.assertEqual(s["attempting_users"],3)
        self.assertEqual(s["solved_users"],2)
        self.assertEqual(s["attempt_count"],5)
