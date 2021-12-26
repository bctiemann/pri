from django.contrib import admin

from marketing.models import NewsItem, SiteContent, NewsletterSubscription


class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'created_at',)
    search_fields = ('subject', 'body',)


class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('page',)


class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'confirmed_at', 'ip',)


admin.site.register(NewsItem, NewsItemAdmin)
admin.site.register(SiteContent, SiteContentAdmin)
admin.site.register(NewsletterSubscription, NewsletterSubscriptionAdmin)