from django.urls import path, include
from . import views

urlpatterns = [
    path('construction_objects/<slug:slug>/contract/materials', views.ContractMaterialsView.as_view(),
         name='contract_materials'),
    path('contract/<slug:slug>/materials', views.MaterialsView.as_view(), name='contract_list_materials'),
    # path('contract/<slug:slug>/search_materials', views.search_materials, name='search_materials'),
    path('release_materials/', views.release_materials, name='release_materials'),
    path('contract/<slug:slug>/released_materials', views.ReleasedMaterialsView.as_view(), name='released_materials'),
    path('return/relesed_materials/<int:id>', views.ReturnReleaseMaterialsView.as_view(),
         name='return_relesed_materials'),
    path('detail/released_materials/<int:id>', views.DetailReleaseMaterialsView.as_view(),
         name='detail_released_materials'),
    path('release_waybill/released_materials/<int:id>', views.AddReleaseWaybillView.as_view(),
         name='add_release_waybill'),
    path('final_waybill/released_materials/<int:id>', views.AddFinalWaybillView.as_view(), name='add_final_waybill'),
    path('construction_objects/<slug:slug>/instruments', views.InstrumentMateriralView.as_view(),
         name='instruments'),
    path('construction_objects/<slug:slug>/released_instruments', views.ReleasedInstruments.as_view(),
         name='released_instruments'),
    path('construction_objects/<slug:slug>/general_base', views.GeneralBaseView.as_view(), name='general_base'),
    path('construction_objects/<slug:slug>/remainder_materials', views.RemainderMaterialsView.as_view(),
         name='remainder_materials'),
    path('writeoff_instruments/', views.writeoff_instruments, name='writeoff_instruments'),
    path('construction_objects/<slug:slug>/writeoff_instruments_list', views.WriteoffInstrumentsList.as_view(), name='writeoff_instruments_list'),
    path('writeoff_instrument/<int:pk>/upload_act_document', views.WriteoffActDocumentUpload.as_view(), name='upload_act_document'),
    path('construction_objects/<slug:slug>/remainder_released_materials', views.RemainderReleasedMaterialsView.as_view(), name='remainder_released_materials'),
    path('transfer_materials/', views.transfer_materials, name='transfer_materials'),
    path('construction_objects/<slug:slug>/transfered_materials_list', views.TransferedMaterialsList.as_view(), name='transfered_materials_list'),
    path('transfered_material/<int:pk>/detail', views.TransferedMaterialsItem.as_view(), name='transfered_materials_item'),
    path('transfer_materials_delivered/', views.transfer_materials_delivered, name='transfer_materials_delivered')

]
