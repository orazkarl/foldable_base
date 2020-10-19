from django.contrib import admin

# Register your models here.
from contracts_app.models import InvoiceForPayment, Contract, RequestForMaterial


# class InvoiceForPaymentInline(admin.TabularInline):
#     model = InvoiceForPayment
#     raw_id_fields = ['contract']
#     extra = 1
#
#
# @admin.register(Contract)
# class ContractAdmin(admin.ModelAdmin):
#     list_display = ['name']
#     prepopulated_fields = {'slug': ('name',)}
#     # inlines = [InvoiceForPaymentInline]
#
#
#
# admin.site.register(InvoiceForPayment)
# admin.site.register(RequestForMaterial)
