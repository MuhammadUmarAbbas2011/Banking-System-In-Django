from django.urls import path
from .views import *
from django.views.generic import TemplateView
urlpatterns = [
    path('', register, name='register'),
    path('login/', login_view, name='login'),
    path('home/',TemplateView.as_view(template_name='home.html'),name='home')
]
