from django.urls import path, include
from . import views

urlpatterns = [
    path('<slug:construction_object>/create/contract', views.ContractCreateView.as_view(), name='contract_create'),
    path('<slug:slug>/update/contract', views.ContractUpdateView.as_view(), name='contract_update'),
    path('<slug:slug>/detail/contract', views.ContractDetailView.as_view(), name='contract_detail'),

    path('<slug:contract>/request/create/', views.RequestForMaterialCreateView.as_view(), name='request_for_material_create'),
    path('request/<int:pk>/update/', views.RequestForMaterialUpdateView.as_view(), name='request_for_material_update'),
    path('request/<int:pk>/detail/', views.RequestForMaterialDetailView.as_view(), name='request_for_material_detail'),
    # path('contract/detail/<slug:slug>', views.ContractDetailView.as_view(), name='contract_detail'),
    # path('contract/edit/<slug:slug>', views.ContractEditView.as_view(), name='contract_edit'),
    # path('contract/<slug:slug>/create', views.ContractCreateView.as_view(), name='contract_add'),

]
