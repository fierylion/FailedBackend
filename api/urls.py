from django.urls import path
from .views import register, login, company, view_upgrade_package
urlpatterns = [
    path('register', register),
    path('login', login),
    path('company/', company),
    path('company/<str:id>', company),
    path('package', view_upgrade_package),
]