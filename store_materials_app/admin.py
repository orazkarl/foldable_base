from django.contrib import admin

# Register your models here.
from .models import ReleasedMaterial, ReleasedMaterialItem, WriteoffInstrumentItem, WriteoffInstrument, TransferMaterial

admin.site.register(ReleasedMaterial)
admin.site.register(ReleasedMaterialItem)
admin.site.register(WriteoffInstrument)
admin.site.register(WriteoffInstrumentItem)
admin.site.register(TransferMaterial)