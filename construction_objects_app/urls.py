from django.urls import path, include
from . import views

urlpatterns = [

    path('', views.HomeView.as_view(), name='home'),
    path('construction_objects/<slug:slug>/<int:pk>', views.ConstructionObjectDetailView.as_view(), name='construction_object_detail'),


    # path('request_for_material/detail/<int:id>', views.RequestForMaterialDetailView.as_view(), name='request_for_material_detail'),
    # path('request_for_material/edit/<int:id>', views.RequestForMaterialEditView.as_view(), name='request_for_material_edit'),
    # path('contract/<slug:slug>/request_for_material/add', views.RequestForMaterialAddView.as_view(), name='request_for_material_add'),

    path('request_for_material/<int:id>/invoice/add', views.InvoiceForPaymentAddView.as_view(), name='invoice_add'),
    path('invoice/edit/<int:id>', views.InvoiceForPaymentEditView.as_view(), name='invoice_edit'),
    path('invoice/delete', views.invoice_delete, name='invoice_delete'),
    path('invoice/detail/<int:id>', views.InvoiceForPaymentDetailView.as_view(), name='invoice_detail'),

    path('invoice/<int:id>/material/add', views.MaterialAddView.as_view(), name='material_add'),
    path('material/edit/<int:id>', views.MaterialEditView.as_view(), name='material_edit'),
    path('material/delete', views.material_delete, name='material_delete'),

    path('send_telegram', views.send_telegram, name='send_telegram'),
    path('invoice_for_payment/<slug:slug>', views.InvoiceForPaymentView.as_view(), name='invoice_for_payment'),

    path('api/telegram/', views.api_telegram_response),

]
