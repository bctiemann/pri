from django.contrib import admin

from consignment.models import Consigner


class ConsignerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name',)


admin.site.register(Consigner, ConsignerAdmin)
