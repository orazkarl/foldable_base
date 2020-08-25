from django.contrib import admin
from .models import Material, ReleaseMaterial, ReleaseMaterialItem

# Register your models here.
admin.site.register(Material)
admin.site.register(ReleaseMaterial)
# admin.site.register(ReleaseMaterialItem)
