from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from questions.services.scoring import automatic_score

class ScoringTests(SimpleTestCase):
    def test_scores(self):
        assert automatic_score(5,5) == Decimal("100.00")
        assert automatic_score(4,5) == Decimal("80.00")
        assert automatic_score(1,3) == Decimal("33.33")
        assert automatic_score(2,7) == Decimal("28.57")
    def test_zero_tests_rejected(self):
        with self.assertRaises(ValidationError): automatic_score(0,0)
