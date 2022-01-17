import uuid

from django.db import models
from django.utils.text import slugify

from users.models import LowercaseEmailField


def get_email_image_path(instance, filename):
    extension = filename.split('.')[-1].lower()
    filename = '{0}.{1}'.format(uuid.uuid4(), extension)
    return 'email_pics/{0}'.format(filename)


class SiteContent(models.Model):
    page = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    content = models.TextField(blank=True)

    def __str__(self):
        return f'{self.page}'


class NewsletterSubscription(models.Model):
    email = LowercaseEmailField(null=True, unique=True)
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.subject)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-created_at',)


class SurveyResponse(models.Model):

    class GeneralRating(models.IntegerChoices):
        RATING_5 = (5, 'Awesome!')
        RATING_4 = (4, 'Good')
        RATING_3 = (3, 'Average')
        RATING_2 = (2, 'Fair')
        RATING_1 = (1, 'Poor')

    class VehicleRating(models.IntegerChoices):
        RATING_5 = (5, 'Awesome!')
        RATING_4 = (4, 'Good')
        RATING_3 = (3, 'Average')
        RATING_2 = (2, 'Fair')
        RATING_1 = (1, 'Poor')

    class RentalFrequency(models.IntegerChoices):
        FREQUENCY_4 = (4, '10+')
        FREQUENCY_3 = (3, '5-10')
        FREQUENCY_2 = (2, '2-5')
        FREQUENCY_1 = (1, 'This was my first')

    class Recommendation(models.IntegerChoices):
        RECOMMEND_3 = (3, 'Yes')
        RECOMMEND_2 = (2, 'Maybe')
        RECOMMEND_1 = (1, 'No')

    class Pricing(models.IntegerChoices):
        PRICING_5 = (5, 'Excellent Value')
        PRICING_4 = (4, 'Good Value')
        PRICING_3 = (3, 'Average')
        PRICING_2 = (2, 'Somewhat High')
        PRICING_1 = (1, 'Very High')
        PRICING_0 = (0, 'No experience with other firms')

    class EmailFrequency(models.IntegerChoices):
        EMAIL_5 = (5, 'Very often')
        EMAIL_4 = (4, 'A few times per month')
        EMAIL_3 = (3, 'Every month')
        EMAIL_2 = (2, 'A few times per year')
        EMAIL_1 = (1, 'Rarely or not at all')

    class VehicleTypes(models.IntegerChoices):
        EXOTICS = (7, 'Exotics (Ferrari, Lamborghini, etc)')
        RACE_CARS = (6, 'Race Cars (Track Driving)')
        SPORTS_CARS = (5, 'Sports Cars (Lotus, Corvette, etc)')
        GRAND_TOURING_CARS = (4, 'Grand Touring Cars')
        PERFORMANCE_LUXURY_CARS = (3, 'Performance Luxury Cars')
        MUSCLE_CARS = (2, 'Muscle Cars')
        CUSTOM_CARS = (1, 'Modified/Custom Cars')
        SPORT_BIKES = (8, 'Sportbikes')
        TOURING_BIKES = (9, 'Touring bikes')
        CRUISING_BIKES = (10, 'Cruising bikes')
        OFF_ROAD_BIKES = (11, 'Off-road bikes/Supermoto/Adventure')

    customer = models.ForeignKey('users.Customer', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    heard_about = models.TextField(blank=True)
    general_rating = models.IntegerField(choices=GeneralRating.choices)
    vehicle_rating = models.IntegerField(choices=VehicleRating.choices)
    rental_frequency = models.IntegerField(choices=RentalFrequency.choices)
    would_recommend = models.IntegerField(choices=Recommendation.choices)
    pricing = models.IntegerField(choices=Pricing.choices)
    email_frequency = models.IntegerField(choices=EmailFrequency.choices)
    vehicle_types = models.IntegerField(choices=VehicleTypes.choices)
    new_vehicles = models.TextField(blank=True)
    comments = models.TextField(blank=True)


class Tweet(models.Model):
    pass


class EmailImage(models.Model):
    image = models.ImageField(width_field='width', height_field='height', upload_to=get_email_image_path)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
