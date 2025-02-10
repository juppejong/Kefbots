# bot/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.settings_view, name='settings'),
    path('history/', views.history_view, name='history'),
    path('strategies/', views.strategies_view, name='strategies'),
    path('autotrade/', views.autotrade_view, name='autotrade'),
    path('autotrade/start/', views.start_autotrade, name='start_autotrade'),
    path('autotrade/stop/', views.stop_autotrade, name='stop_autotrade'),
    path('get_logs/', views.get_logs, name='get_logs'),  # Voeg deze regel toe voor AJAX
    path('get_rsi_graph/', views.get_rsi_graph, name='get_rsi_graph'),
    path('get_ma_crossover_graph/', views.get_ma_crossover_graph, name='get_ma_crossover_graph'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('about/', views.about_view, name='about'),

]

