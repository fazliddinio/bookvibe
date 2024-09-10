from django.urls import path
from . import views

app_name = "feedback"

urlpatterns = [
    path("submit/", views.FeedbackView.as_view(), name="submit"),
]
