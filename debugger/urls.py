from django.urls import path

from . import views


app_name = "debugger"

urlpatterns = [
    path("", views.index, name="index"),
    path("__demo__/post/<int:pk>/", views.demo_detail, name="demo-detail"),
    path("__demo__/intentional-failure/", views.intentional_failure, name="intentional-failure"),
]
