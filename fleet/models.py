import uuid
import os
import json
import time

from encrypted_fields import fields
from django_countries.fields import CountryField
from PIL import Image
from io import BytesIO
from phonenumber_field.modelfields import PhoneNumberField
from precise_bbcode.bbcode import get_parser

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


# TextChoices and IntegerChoices are enum classes with internal and verbose values; if a CharField is set to use
# this object for its choices, it will be represented in the admin with a select dropdown of acceptable values.

class VehicleType(models.IntegerChoices):
    CAR = (1, 'Road Car')
    BIKE = (2, 'Motorcycle')
    TRACK = (3, 'Track Car')


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

# Vehicle is the "back-end" representation of a physical vehicle, with potentially sensitive information attached.
class Vehicle(models.Model):

    # Multiple Vehicles can link to the same VehicleMarketing.
    # Cannot be a ForeignKey because the databases are kept segregated. See pri/db_routers.py
    vehicle_marketing_id = models.IntegerField(null=True, blank=True, help_text='ID of VehicleMarketing object this corresponds to')

    # Fields defined on the model correspond to database columns and fully define their behavior both in DB and in code.
    # Model field names should be verbose, specific, and expressive; i.e. "vehicle_type" rather than "vtype"
    # Note that an auto-incrementing integer "id" field is implicit in all models, unless overridden using the
    # "primary_key" parameter on a custom defined field
    # https://docs.djangoproject.com/en/3.1/ref/models/fields/
    make = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)
    slug = models.SlugField(max_length=50, blank=True)
    vehicle_type = models.IntegerField(choices=VehicleType.choices, default=VehicleType.CAR)
    status = models.IntegerField(choices=VehicleStatus.choices, default=VehicleStatus.BUILDING)
    external_owner = models.ForeignKey('consignment.Consigner', null=True, blank=True, on_delete=models.SET_NULL)
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
        return VehicleMarketing.objects.get(pk=self.vehicle_marketing_id)

    @property
    def due_services(self):
        services = self.scheduledservice_set.all()
        services = services.filter(is_due=True)
        return services

    @property
    def upcoming_services(self):
        services = self.scheduledservice_set.all()
        upcoming_threshold_miles = self.mileage + 500
        services = services.filter(next_mileage__lte=upcoming_threshold_miles)
        services = services.filter(done_at__isnull=True, done_mileage__isnull=True)
        return services
        """
        AND (nextmiles <= <CFQUERYPARAM value="#Vehicles.mileage#" CFSQLType="CF_SQL_INTEGER"> + 500 AND donestamp IS NULL AND donemiles IS NULL)
        """

    # TODO: Either expose the slug in the backoffice vehicle form and make it controllable, or add collision
    # checking to this method for creating new records
    def get_slug(self):
        return slugify(f'{self.make} {self.model}')

    # This is the string representation of the vehicle object; will be used in the admin, templates, etc. as a default
    def __str__(self):
        return f'[{self.id}] {self.vehicle_name}'

    # Meta subclass is used for defining attributes like default ordering
    class Meta:
        ordering = ('year',)


# VehicleMarketing is the "front-end" representation of a vehicle, which contains no sensitive information.
class VehicleMarketing(models.Model):

    # Used for textual representations in ad copy
    VEHICLE_TYPE_MAP = {
        VehicleType.CAR: 'car',
        VehicleType.BIKE: 'bike',
        VehicleType.TRACK: 'track car',
    }

    # These fields are redundant with the Vehicle class, and will be updated concurrently with that table when
    # edited via the backoffice form. This is to avoid any joins or queries against the Vehicle table when pulling
    # data for the front-end site.
    make = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)
    slug = models.SlugField(max_length=50, blank=True)
    vehicle_type = models.IntegerField(choices=VehicleType.choices, default=VehicleType.CAR)
    status = models.IntegerField(choices=VehicleStatus.choices, default=VehicleStatus.BUILDING)
    weighting = models.IntegerField(null=True, blank=True)

    # Hero shot (front page)
    showcase_image = models.ImageField(null=True, blank=True, width_field='showcase_width', height_field='showcase_height', upload_to=get_vehicle_picture_path)
    showcase_width = models.IntegerField(null=True, blank=True)
    showcase_height = models.IntegerField(null=True, blank=True)

    # Fleet page side view image
    thumbnail_image = models.ImageField(null=True, blank=True, width_field='thumbnail_width', height_field='thumbnail_height', upload_to=get_vehicle_picture_path)
    thumbnail_width = models.IntegerField(null=True, blank=True)
    thumbnail_height = models.IntegerField(null=True, blank=True)

    # Mobile app vehicle listing table icon
    mobile_thumbnail_image = models.ImageField(null=True, blank=True, width_field='mobile_thumbnail_width', height_field='mobile_thumbnail_height', upload_to=get_vehicle_picture_path)
    mobile_thumbnail_width = models.IntegerField(null=True, blank=True)
    mobile_thumbnail_height = models.IntegerField(null=True, blank=True)

    # Vector from multiple angles, used for marking damage on rentals
    inspection_image = models.ImageField(null=True, blank=True, width_field='inspection_width', height_field='inspection_height', upload_to=get_vehicle_picture_path)
    inspection_width = models.IntegerField(null=True, blank=True)
    inspection_height = models.IntegerField(null=True, blank=True)

    # These fields are for public display/marketing purposes only and are not sensitive.
    horsepower = models.IntegerField(null=True, blank=True)
    torque = models.IntegerField(null=True, blank=True)
    top_speed = models.IntegerField(null=True, blank=True)
    transmission_type = models.CharField(choices=TransmissionType.choices, max_length=12, default=TransmissionType.MANUAL)
    gears = models.IntegerField(null=True, blank=True)
    location = models.CharField(choices=Location.choices, max_length=12, default=Location.NEW_YORK)
    tight_fit = models.BooleanField(default=False)
    blurb = models.TextField(blank=True)
    specs = models.JSONField(null=True, blank=True, help_text='JSON format')
    origin_country = CountryField(blank=True)

    # Price fields
    price_per_day = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    discount_2_day = models.IntegerField(null=True, blank=True, verbose_name='2-day discount', help_text='Percent')
    discount_3_day = models.IntegerField(null=True, blank=True, verbose_name='3-day discount', help_text='Percent')
    discount_7_day = models.IntegerField(null=True, blank=True, verbose_name='7-day discount', help_text='Percent')
    security_deposit = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    miles_included = models.IntegerField(null=True, blank=True, help_text='Per day')

    # In the event of multiple vehicles matching this marketing representation, we pick the first one per the
    # Meta.ordering setting
    @property
    def vehicle(self):
        return Vehicle.objects.filter(vehicle_marketing_id=self.id).first()

    @property
    def vehicle_name(self):
        return f'{self.year} {self.make} {self.model}'

    # For use in marketing copy
    @property
    def vehicle_type_casual(self):
        return self.VEHICLE_TYPE_MAP.get(self.vehicle_type)

    @property
    def headline(self):
        if self.specs:
            return self.specs.get('headline') or ''
        return ''

    @property
    def specs_json(self):
        return json.dumps(self.specs)

    @property
    def extra_miles_choices(self):
        return list(settings.EXTRA_MILES_PRICES.values())

    @property
    def extra_miles_overage_per_mile(self):
        return settings.EXTRA_MILES_OVERAGE_PER_MILE

    @property
    def military_discount_pct(self):
        return settings.MILITARY_DISCOUNT_PCT

    @property
    def blurb_parsed(self):
        parser = get_parser()
        return parser.render(self.blurb)

    def get_multi_day_discounted_price(self, num_days):
        discount_pct = getattr(self, f'discount_{num_days}_day', 0)
        return float(self.price_per_day) * num_days * (1 - discount_pct / 100)

    def get_multi_day_miles_included(self, num_days):
        return self.miles_included * num_days

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

    class Meta:
        ordering = ('-is_first',)


class VehicleVideo(models.Model):
    vehicle_marketing = models.ForeignKey('fleet.VehicleMarketing', null=True, on_delete=models.CASCADE, related_name='vids')
    video_mp4 = models.FileField(blank=True, upload_to=get_vehicle_video_path)
    video_webm = models.FileField(blank=True, upload_to=get_vehicle_video_path)
    file_extension = models.CharField(max_length=4, blank=True)
    poster = models.ImageField(blank=True, width_field='poster_width', height_field='poster_height', upload_to=get_vehicle_picture_path)
    poster_width = models.IntegerField(null=True, blank=True)
    poster_height = models.IntegerField(null=True, blank=True)
    thumbnail = models.ImageField(blank=True, width_field='thumb_width', height_field='thumb_height', upload_to=get_vehicle_picture_path)
    thumb_width = models.IntegerField(null=True, blank=True)
    thumb_height = models.IntegerField(null=True, blank=True)
    thumb_extension = models.CharField(max_length=4, blank=True)
    length = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    blurb = models.TextField(blank=True)
    is_first = models.BooleanField(default=False)

    # Currently this is a stub, as we have no videos. We may need to build this out better to improve the workflow of
    # uploading new videos, but for now the admin can be used to populate them manually.
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def length_formatted(self):
        return time.strftime('%M:%S', time.gmtime(self.length))

    class Meta:
        ordering = ('-is_first',)


class TollTag(models.Model):
    toll_account = models.CharField(max_length=32, blank=True)
    tag_number = models.CharField(max_length=32, blank=True)
    vehicle = models.ForeignKey('fleet.Vehicle', null=True, blank=True, on_delete=models.SET_NULL)
    alt_usage = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.tag_number} ({self.label})'

    @property
    def label(self):
        if self.vehicle:
            return self.vehicle.vehicle_name
        elif self.alt_usage:
            return self.alt_usage
        return 'Unassigned'

    class Meta:
        ordering = ('tag_number',)
