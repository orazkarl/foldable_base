from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Object, Contract, Material

# admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Material)
