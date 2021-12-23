from django.db import models


class NewsletterSubscription(models.Model):
    pass


class NewsItem(models.Model):
    author_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, blank=True, db_index=True)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)

    @property
    def year(self):
        return self.created_at.year

    class Meta:
        ordering = ('-created_at',)


class SurveyResponse(models.Model):
    pass


class Tweet(models.Model):
    pass
