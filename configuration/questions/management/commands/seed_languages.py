from django.core.management.base import BaseCommand
from django.utils.text import slugify
from questions.models import Language

LANGUAGES = [
    ("Python","python","python",True),
    ("JavaScript","javascript","javascript",True),
    ("HTML","html","html",False),
    ("CSS","css","css",False),
    ("SQL","sql","sql",False),
    ("Django","django","django",False),
    ("Django REST Framework","django-rest-framework","drf",False),
    ("Turtle","turtle","turtle",False),
    ("Tkinter","tkinter","tkinter",False),
]

class Command(BaseCommand):
    help="Create the default question languages."
    def handle(self,*args,**kwargs):
        for name,slug,code,auto in LANGUAGES:
            Language.objects.update_or_create(slug=slug,defaults={"name":name,"code":code,"supports_automatic_testing":auto})
        self.stdout.write(self.style.SUCCESS("Question languages seeded."))
