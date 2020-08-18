from django.urls import path, include
from . import views

urlpatterns = [
    path('add_materials/invoice/<int:id>', views.AddMaterialView.as_view(), name='add_material'),
    path('objects/<slug:slug>/paid_materials', views.PaidMaterailsView.as_view(), name='paid_materials'),
    path('objects/<slug:slug>/materials', views.MaterialsView.as_view(), name='materials'),
    path('objects/invoice/<int:id>/materials', views.InvoicePaidMaterialsView.as_view(), name='invoice_materials'),
    path('marriage_materials/', views.marriage_materials, name='marriage_materials'),
    path('return_materials/', views.return_materials, name='return_materials'),
]
