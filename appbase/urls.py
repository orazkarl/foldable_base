from django.urls import path, include
from . import views

urlpatterns = [

    path('', views.HomeView.as_view(), name='home'),
    path('objects/<slug:slug>', views.ObjectDetailView.as_view(), name='object_detail'),
    path('objects/<slug:slug>/<slug:contract_slug>', views.ContractDetailView.as_view(), name='contract_detail'),
    path('objects/<slug:slug>/<slug:contract_slug>/edit', views.ContractEditView.as_view(), name='contract_edit'),
    path('objects/<slug:slug>/contract/add', views.ContractAddView.as_view(), name='contract_add'),
    path('objects/<slug:slug>/contract/delete', views.contract_delete, name='contract_delete'),

]
