import uuid
import os

from encrypted_fields import fields
from django_countries.fields import CountryField
from PIL import Image
from io import BytesIO
from phonenumber_field.modelfields import PhoneNumberField

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


# TextChoices and IntegerChoices are enum classes with internal and verbose values; if a CharField is set to use
# this object for its choices, it will be represented in the admin with a select dropdown of acceptable values.

class VehicleType(models.TextChoices):
    CAR = ('car', 'Road Car')
    BIKE = ('bike', 'Bike')
    TRACK = ('track', 'Track Car')


class VehicleStatus(models.IntegerChoices):
    BUILDING = (0, 'Building')
    READY = (1, 'Ready')
    DOWN = (2, 'Damaged / Repairing')
    OUT_OF_SERVICE = (3, 'Out Of Service')


class TransmissionType(models.TextChoices):
    MANUAL = ('manual', 'Manual')  # 1
    SEMI_AUTO = ('semi_auto', 'Semi-Auto')  # 2
    AUTO = ('auto', 'Automatic')  # 3


class Location(models.TextChoices):
    NEW_YORK = ('new_york', 'New York')
    TAMPA = ('tampa', 'Tampa')


# Helper methods for providing custom upload locations for media

def get_vehicle_picture_path(instance, filename):
    extension = filename.split('.')[-1].lower()
    filename = '{0}.{1}'.format(uuid.uuid4(), extension)
    return 'pics/{0}'.format(filename)


def get_vehicle_video_path(instance, filename):
    extension = filename.split('.')[-1].lower()
    filename = '{0}.{1}'.format(uuid.uuid4(), extension)
    return 'vids/{0}'.format(filename)


# Model classes

class Vehicle(models.Model):

    # Fields defined on the model correspond to database columns and fully define their behavior both in DB and in code.
    # Model field names should be verbose, specific, and expressive; i.e. "vehicle_type" rather than "vtype"
    # Note that an auto-incrementing integer "id" field is implicit in all models, unless overridden using the
    # "primary_key" parameter on a custom defined field
    # https://docs.djangoproject.com/en/3.1/ref/models/fields/
    make = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)
    id_old = models.IntegerField(null=True, blank=True)
    vehicle_type = models.CharField(choices=VehicleType.choices, max_length=20)
    status = models.IntegerField(choices=VehicleStatus.choices, default=VehicleStatus.BUILDING)
    created_at = models.DateTimeField(auto_now_add=True)
    acquired_on = models.DateField(null=True, blank=True)
    relinquished_on = models.DateField(null=True, blank=True)
    plate = models.CharField(max_length=10, blank=True)
    vin = models.CharField(max_length=50, blank=True)
    mileage = models.IntegerField(null=True, blank=True)
    damage = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    policy_number = fields.EncryptedCharField(max_length=255, blank=True)
    policy_company = models.CharField(max_length=255, blank=True)
    policy_phone = PhoneNumberField(blank=True)
    weighting = models.IntegerField(null=True, blank=True)
    redirect_to = models.ForeignKey('fleet.Vehicle', null=True, blank=True, on_delete=models.SET_NULL)

    # Example of a model property which produces a derived value (requires no params other than self), and thus is
    # referenced as a property rather than being invoked as a method (with parentheses) - vehicle.vehicle_name
    @property
    def vehicle_name(self):
        return f'{self.year} {self.make} {self.model}'

    @property
    def vehicle_marketing(self):
        return VehicleMarketing.objects.filter(vehicle_id=self.id).first()

    # This is the string representation of the vehicle object; will be used in the admin, templates, etc. as a default
    def __str__(self):
        return f'[{self.id}] {self.vehicle_name}'

    # Meta subclass is used for defining attributes like default ordering
    class Meta:
        ordering = ('year',)


class VehicleMarketing(models.Model):

    # This links the record to the Vehicle object, which is where potentially sensitive business data
    # is stored. Cannot be a ForeignKey because the databases are kept segregated. See pri/db_routers.py
    vehicle_id = models.IntegerField(null=True, blank=True, help_text='ID of Vehicle object this corresponds to')
    slug = models.SlugField(max_length=50, blank=True)
    weighting = models.IntegerField(null=True, blank=True)

    showcase_image = models.ImageField(blank=True, width_field='showcase_width', height_field='showcase_height', upload_to=get_vehicle_picture_path)
    showcase_width = models.IntegerField(null=True, blank=True)
    showcase_height = models.IntegerField(null=True, blank=True)

    # These fields are redundant with the Vehicle class, and will be updated concurrently with that table when
    # edited via the backoffice form. This is to avoid any joins or queries against the Vehicle table when pulling
    # data for the front-end site.
    make = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)
    vehicle_type = models.CharField(choices=VehicleType.choices, max_length=20)
    status = models.IntegerField(choices=VehicleStatus.choices, default=VehicleStatus.BUILDING)

    # These fields are for public display/marketing purposes only and are not sensitive.
    horsepower = models.IntegerField(null=True, blank=True)
    torque = models.IntegerField(null=True, blank=True)
    top_speed = models.IntegerField(null=True, blank=True)
    transmission_type = models.CharField(choices=TransmissionType.choices, max_length=12, blank=True)
    gears = models.IntegerField(null=True, blank=True)
    location = models.CharField(choices=Location.choices, max_length=12, blank=True, default=Location.NEW_YORK)
    tight_fit = models.BooleanField(default=False)
    blurb = models.TextField(blank=True)
    specs = models.JSONField(null=True, blank=True, help_text='JSON format')
    origin_country = CountryField(blank=True)

    # Price fields
    price_per_day = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    discount_2_day = models.IntegerField(null=True, blank=True, verbose_name='2-day discount', help_text='Percent')
    discount_3_day = models.IntegerField(null=True, blank=True, verbose_name='3-day discount', help_text='Percent')
    discount_7_day = models.IntegerField(null=True, blank=True, verbose_name='7-day discount', help_text='Percent')
    deposit = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    miles_included = models.IntegerField(null=True, blank=True, help_text='Per day')

    @property
    def vehicle_name(self):
        return f'{self.year} {self.make} {self.model}'

    @property
    def headline(self):
        return self.specs.get('headline')

    def get_slug(self):
        return slugify(f'{self.make} {self.model}')

    def __str__(self):
        return f'[{self.id}] {self.vehicle_name}'


class VehiclePicture(models.Model):
    IMAGE_FORMAT_MAP = {
        'image/jpeg': 'JPEG',
        'image/png': 'PNG',
    }

    vehicle_marketing = models.ForeignKey('fleet.VehicleMarketing', null=True, on_delete=models.CASCADE, related_name='pics')
    image = models.ImageField(blank=True, width_field='width', height_field='height', upload_to=get_vehicle_picture_path)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    thumbnail = models.ImageField(blank=True, width_field='thumb_width', height_field='thumb_height', upload_to=get_vehicle_picture_path)
    thumb_width = models.IntegerField(null=True, blank=True)
    thumb_height = models.IntegerField(null=True, blank=True)
    is_first = models.BooleanField(default=False)

    # Override save method to post-process the uploaded image/thumbnail
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            try:
                image = Image.open(self.image.path)
            except:
                return False

            # Resize uploaded image if larger than the main limits
            if image.width > settings.PIC_MAX_WIDTH or image.height > settings.PIC_MAX_HEIGHT:
                pic_size = (settings.PIC_MAX_WIDTH, settings.PIC_MAX_HEIGHT)

                image.thumbnail(pic_size)
                image.save(self.image.path)
                self.width = image.width
                self.height = image.height
                super().save(*args, **kwargs)

            # Then, if there is no thumbnail, make a copy and resize
            if not self.thumbnail:
                thumb_size = (settings.THUMB_MAX_WIDTH, settings.THUMB_MAX_HEIGHT)
                format_mime_type = image.get_format_mimetype()
                thumb_format = self.IMAGE_FORMAT_MAP.get(format_mime_type, 'JPEG')

                image.thumbnail(thumb_size)
                temp_thumb = BytesIO()
                image.save(temp_thumb, thumb_format, quality=90)
                temp_thumb.seek(0)
                self.thumbnail.save(self.image.name, ContentFile(temp_thumb.read()), save=True)
                temp_thumb.close()
                super().save(*args, **kwargs)


class VehicleVideo(models.Model):
    pass


class TollTag(models.Model):
    pass
