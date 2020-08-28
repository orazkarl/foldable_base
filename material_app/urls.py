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
    # path('contract/<slug:slug>/search_materials', views.search_materials, name='search_materials'),
    path('release_materials/', views.release_materials, name='release_materials'),
    path('contract/<slug:slug>/relesed_materials', views.ReleaseMaterialsView.as_view(), name='relesed_materials'),
    path('return/relesed_materials/<int:id>', views.ReturnReleaseMaterialsView.as_view(), name='return_relesed_materials'),
    path('detail/relesed_materials/<int:id>', views.DetailReleaseMaterialsView.as_view(), name='detail_relesed_materials'),
    path('release_waybill/relesed_materials/<int:id>', views.AddReleaseWaybillView.as_view(), name='add_release_waybill'),
    path('final_waybill/relesed_materials/<int:id>', views.AddFinalWaybillView.as_view(), name='add_final_waybill'),
    path('objects/<slug:slug>/instruments', views.InstrumentMateriralView.as_view(), name='instruments'),
    path('objects/<slug:slug>/general_base', views.GeneralBaseView.as_view(), name='general_base'),
    path('objects/<slug:slug>/remainder_materials', views.RemainderMaterialsView.as_view(), name='remainder_materials'),
]
