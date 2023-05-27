from django.urls import path
from . import test_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('history/', views.history, name='history'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
