from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('account/<int:account_id>/', views.account_details, name='account_details'),
    path('transfer/', views.transfer_money, name='transfer'),
    path('search/', views.search_transactions, name='search_transactions'),
]