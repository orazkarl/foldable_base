from django.urls import path, include
from . import views

urlpatterns = [
    path('<slug:construction_object>/create/', views.ContractCreateView.as_view(), name='contract_create'),
    # path('contract/detail/<slug:slug>', views.ContractDetailView.as_view(), name='contract_detail'),
    # path('contract/edit/<slug:slug>', views.ContractEditView.as_view(), name='contract_edit'),
    # path('contract/<slug:slug>/create', views.ContractCreateView.as_view(), name='contract_add'),

]
