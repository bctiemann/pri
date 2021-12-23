from django.contrib import admin

from marketing.models import NewsItem


class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'created_at',)
    search_fields = ('subject', 'body',)


admin.site.register(NewsItem, NewsItemAdmin)
