from django.db import models


class NewsletterSubscription(models.Model):
    pass


class NewsItem(models.Model):
    author_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)

    class Meta:
        ordering = ('-created_at',)


class SurveyResponse(models.Model):
    pass


class Tweet(models.Model):
    pass
