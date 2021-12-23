from django.contrib import admin

from marketing.models import NewsItem, SiteContent


class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'created_at',)
    search_fields = ('subject', 'body',)


class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('page',)


admin.site.register(NewsItem, NewsItemAdmin)
admin.site.register(SiteContent, SiteContentAdmin)
