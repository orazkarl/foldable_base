from django.urls import path, include
from . import views

urlpatterns = [
    path('construction_objects/<slug:slug>/analytics', views.AnalyticsView.as_view(), name='analytics'),
    path('construction_objects/<slug:slug>/total_stats', views.TotalStats.as_view(), name='total_stats'),
    path('construction_objects/<slug:slug>/released_material_stats', views.ReleasedMaterialsStats.as_view(), name='released_material_stats'),
    path('construction_objects/<slug:slug>/analytics/export', views.export_analytics, name='export_analytics'),
]
