from django.contrib import admin

from backoffice.models import BBSPost


class BBSPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'created_at',)


admin.site.register(BBSPost, BBSPostAdmin)
