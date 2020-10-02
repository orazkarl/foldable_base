from django.urls import path, include
from . import views

urlpatterns = [
    path('add_materials/invoice/<int:id>', views.AddMaterialView.as_view(), name='add_material'),
    path('construction_objects/<slug:slug>/paid_materials', views.PaidMaterailsView.as_view(), name='paid_materials'),
    path('construction_objects/invoice/<int:id>/paid_materials_app', views.InvoicePaidMaterialsView.as_view(),
         name='invoice_materials'),

    path('marriage_materials/', views.marriage_materials, name='marriage_materials'),
    path('return_materials/', views.return_materials, name='return_materials'),
]
