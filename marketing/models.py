from django.db import models


class NewsletterSubscription(models.Model):
    pass


class NewsItem(models.Model):
    created_by = models.ForeignKey('users.User', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)

    class Meta:
        ordering = ('-created_at',)


class SurveyResponse(models.Model):
    pass


class Tweet(models.Model):
    pass
