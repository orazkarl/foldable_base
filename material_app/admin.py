from django.contrib import admin
from .models import Material, ReleasedMaterial, ReleasedMaterialItem


admin.site.register(Material)
admin.site.register(ReleasedMaterial)
admin.site.register(ReleasedMaterialItem)
