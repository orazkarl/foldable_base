from django.urls import path, include
from . import views
urlpatterns = [

    path('', views.HomeView.as_view(), name='home'),
    path('objects/<slug:slug>', views.ObjectDetailView.as_view(), name='object_detail'),
path('objects/<slug:slug>/<slug:contract_slug>', views.ContractDetailView.as_view(), name='contract_detail'),

]