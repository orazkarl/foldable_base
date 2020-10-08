from django.urls import path, include
from . import views

urlpatterns = [
    path('add_materials/invoice/<int:id>', views.AddMaterialsExcelView.as_view(), name='add_material'),

    path('<int:pk>/material/create', views.MaterialCreateView.as_view(), name='material_create'),
    path('material/<int:pk>/update/', views.MaterialUpdateView.as_view(), name='material_update'),

    path('construction_objects/<slug:slug>/paid_materials', views.PaidMaterailsView.as_view(), name='paid_materials'),
    path('construction_objects/invoice/<int:id>/paid_materials', views.InvoicePaidMaterialsView.as_view(),
         name='invoice_materials'),

    path('marriage_materials/', views.marriage_materials, name='marriage_materials'),
    path('return_materials/', views.return_materials, name='return_materials'),
    path('material/delete', views.material_delete, name='material_delete'),
]
