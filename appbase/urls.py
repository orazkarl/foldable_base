from django.urls import path, include
from . import views

urlpatterns = [

    path('', views.HomeView.as_view(), name='home'),
    path('objects/<slug:slug>/<int:pk>', views.ObjectDetailView.as_view(), name='object_detail'),

    path('contract/detail/<slug:slug>', views.ContractDetailView.as_view(), name='contract_detail'),
    path('contract/edit/<slug:slug>', views.ContractEditView.as_view(), name='contract_edit'),
    path('contract/<slug:slug>/add', views.ContractAddView.as_view(), name='contract_add'),
    path('contract/delete', views.contract_delete, name='contract_delete'),

    path('request/detail/<int:id>', views.RequestDetailView.as_view(), name='request_detail'),
    path('request/edit/<int:id>', views.RequestEditView.as_view(), name='request_edit'),
    path('contract/<slug:slug>/request/add', views.RequestAddView.as_view(), name='request_add'),
    path('request/delete', views.request_delete, name='request_delete'),

    path('request/<int:id>/invoice/add', views.InvoiceAddView.as_view(), name='invoice_add'),
    path('invoice/edit/<int:id>', views.InvoiceEditView.as_view(), name='invoice_edit'),
    path('invoice/delete', views.invoice_delete, name='invoice_delete'),

    path('send_telegram', views.send_telegram, name='send_telegram'),

    path('invoice_for_payment/<slug:slug>', views.InvoiceForPaymentView.as_view(), name='invoice_for_payment'),
    path('add_materials/contract/<slug:slug>', views.AddMaterialView.as_view(), name='add_material'),

    path('objects/<slug:slug>/paid_materials', views.PaidMaterailsView.as_view(), name='paid_materials'),
    path('objects/<slug:slug>/materials', views.MaterialsView.as_view(), name='materials'),

    path('api/telegram/', views.api_telegram_response)


]
