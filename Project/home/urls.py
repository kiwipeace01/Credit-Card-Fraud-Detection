from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('register_card/', views.reg_card, name='register_card'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transaction/', views.transaction, name='transaction'),
    path('admin/', views.admin, name='admin')
]