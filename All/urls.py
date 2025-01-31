from django.urls import path
from .views import *
from django.views.generic import TemplateView
urlpatterns = [
    path('', register, name='register'),
    path('login/', login_view, name='login'),
    path('home/',TemplateView.as_view(template_name='home.html'),name='home'),
    path('check-account-balance/',check_account_balance,name='check-account-balance'),
    path('deposit-money/',deposit_money,name='deposit-money'),
    path('withdraw-money/', withdraw_money, name='withdraw-money'),
    path('logout/',logout_view,name='logout')
]
