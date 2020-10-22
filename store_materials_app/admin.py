from django.conf.urls import url
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html


from .models import ReleasedMaterial, ReleasedMaterialItem, WriteoffInstrumentItem, WriteoffInstrument, TransferMaterial

admin.site.register(ReleasedMaterial)
admin.site.register(ReleasedMaterialItem)
# admin.site.register(WriteoffInstrument)
# admin.site.register(WriteoffInstrumentItem)


# admin.site.register(TransferMaterial)
@admin.register(TransferMaterial)
class TransferMaterialAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'from_construction_object', 'to_construction_object', 'created_at', 'is_access',
                    'transfermaterial_actions']

    def get_urls(self):
        urls = super().get_urls()
        custom_url = [
            url(r'^(?P<transfermaterial_id>.+)/transfer/$',
                self.admin_site.admin_view(self.process_transfer),
                name='transfer_material_admin'),
        ]
        return custom_url + urls

    def transfermaterial_actions(self, obj):
        return format_html('<a class="button" href="{}">Перевод</a>',
                           reverse('admin:transfer_material_admin', args=[obj.pk]))

    def process_transfer(self, request, transfermaterial_id, *args, **kwargs):
        transfermaterial = self.get_object(request, transfermaterial_id)
        transfermaterial.is_access = True
        transfermaterial.save()
        return redirect('/admin/store_materials_app/transfermaterial/')
