from django.db import models

from users.models import LowercaseEmailField


class SiteContent(models.Model):
    page = models.CharField(max_length=100)
    content = models.TextField(blank=True)

    def __str__(self):
        return f'{self.page}'


class NewsletterSubscription(models.Model):
    email = LowercaseEmailField(null=True)
    full_name = models.CharField(max_length=255)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    hash = models.UUIDField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class NewsItem(models.Model):
    author_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, blank=True, db_index=True)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)

    def __str__(self):
        return f'{self.id} {self.created_at.date()} {self.slug}'

    class Meta:
        ordering = ('-created_at',)


class SurveyResponse(models.Model):
    pass


class Tweet(models.Model):
    pass
