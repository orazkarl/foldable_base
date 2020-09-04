from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Object, Contract, InvoiceForPayment, RequestForMaterial



admin.site.unregister(Group)
admin.site.site_header = "АДМИН ПАНЕЛЬ"
admin.site.site_title = "АДМИН ПАНЕЛЬ"
# admin.site.index_title = "АДМИН ПАНЕЛЬ"

@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}


class InvoiceForPaymentInline(admin.TabularInline):
    model = InvoiceForPayment
    raw_id_fields = ['contract']
    extra = 1


# @admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}
    # inlines = [InvoiceForPaymentInline]



# admin.site.register(InvoiceForPayment)
# admin.site.register(RequestForMaterial)

from allauth.socialaccount.admin import SocialApp, SocialAccount,SocialToken
from allauth.account.admin import EmailAddress
from django.contrib.sites.models import Site

admin.site.unregister(SocialApp)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)
admin.site.unregister(EmailAddress)
admin.site.unregister(Site)