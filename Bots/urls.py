# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = 'Bots'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/<slug:slug>/stats/', views.bot_stats_api, name='bot_stats_api'),
    path('api/<slug:slug>/runs/', views.bot_runs_api, name='bot_runs_api'),
]
