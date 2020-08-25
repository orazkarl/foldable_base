from django.urls import path, include
from . import views

urlpatterns = [
    path('add_materials/invoice/<int:id>', views.AddMaterialView.as_view(), name='add_material'),
    path('objects/<slug:slug>/paid_materials', views.PaidMaterailsView.as_view(), name='paid_materials'),
    path('objects/invoice/<int:id>/materials', views.InvoicePaidMaterialsView.as_view(), name='invoice_materials'),
    path('marriage_materials/', views.marriage_materials, name='marriage_materials'),
    path('return_materials/', views.return_materials, name='return_materials'),
    path('objects/<slug:slug>/contract/materials', views.ContractMaterialsView.as_view(), name='contract_materials'),
    path('contract/<slug:slug>/materials', views.MaterialsView.as_view(), name='contract_list_materials'),
    path('release_materials/', views.release_materials, name='release_materials'),
    path('contract/<slug:slug>/relesed_materials', views.ReleaseMaterialsView.as_view(), name='relesed_materials'),
    path('detail/relesed_materials/<int:id>', views.DetailReleaseMaterialsView.as_view(), name='detail_relesed_materials'),
]
