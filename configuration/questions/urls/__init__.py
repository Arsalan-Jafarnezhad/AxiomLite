from django.urls import include, path
app_name="questions"
urlpatterns=[
    path("",include("questions.urls.public")),
    path("api/",include("questions.api.urls")),
    path("submissions/",include("questions.urls.submission")),
]
