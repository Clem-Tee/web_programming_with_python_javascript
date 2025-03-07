from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:name>", views.greet, name="greet"),
    path("clem", views.clem, name="clem"),
    path("david", views.david, name="david")
]
