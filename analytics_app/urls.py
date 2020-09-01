from django.urls import path, include
from . import views

urlpatterns = [
    path('objects/<slug:slug>/analytics', views.AnalyticsView.as_view(), name='analytics'),
]
