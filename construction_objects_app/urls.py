from django.urls import path, include
from . import views

urlpatterns = [

    path('', views.HomeView.as_view(), name='home'),
    path('construction_objects/<slug:slug>/<int:pk>', views.ConstructionObjectDetailView.as_view(),
         name='construction_object_detail'),

    path('invoice_for_payment/<slug:slug>', views.InvoiceForPaymentView.as_view(), name='invoice_for_payment'),

    path('invoice/<int:id>/material/add', views.MaterialAddView.as_view(), name='material_add'),
    path('material/edit/<int:id>', views.MaterialEditView.as_view(), name='material_edit'),
    path('material/delete', views.material_delete, name='material_delete'),

    path('send_telegram', views.send_telegram, name='send_telegram'),
    path('api/telegram/', views.api_telegram_response),

]
