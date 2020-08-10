from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Object, Contract, Material, InvoiceForPayment

admin.site.unregister(Group)


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}


class InvoiceForPaymentInline(admin.TabularInline):
    model = InvoiceForPayment
    raw_id_fields = ['contract']
    extra = 1


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}
    # inlines = [InvoiceForPaymentInline]


admin.site.register(Material)
