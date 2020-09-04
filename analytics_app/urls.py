from django.urls import path, include
from . import views

urlpatterns = [
    path('objects/<slug:slug>/analytics', views.AnalyticsView.as_view(), name='analytics'),
    path('objects/<slug:slug>/total_stats', views.TotalStats.as_view(), name='total_stats'),
    path('objects/<slug:slug>/release_mat_stats', views.ReleaseMaterialsStats.as_view(), name='release_mat_stats'),
    path('objects/<slug:slug>/analytics/export', views.export_analytics, name='export_analytics'),
]
