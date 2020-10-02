from django.contrib import admin

# Register your models here.
from .models import ReleasedMaterial, ReleasedMaterialItem

admin.site.register(ReleasedMaterial)
admin.site.register(ReleasedMaterialItem)