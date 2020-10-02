from django.contrib import admin
from django.contrib.auth.models import Group
from .models import ConstructionObject



admin.site.unregister(Group)
admin.site.site_header = "АДМИН ПАНЕЛЬ"
admin.site.site_title = "АДМИН ПАНЕЛЬ"
# admin.site.index_title = "АДМИН ПАНЕЛЬ"

@admin.register(ConstructionObject)
class ConstructionObjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    prepopulated_fields = {'slug': ('name',)}



from allauth.socialaccount.admin import SocialApp, SocialAccount,SocialToken
from allauth.account.admin import EmailAddress
from django.contrib.sites.models import Site

admin.site.unregister(SocialApp)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)
admin.site.unregister(EmailAddress)
admin.site.unregister(Site)