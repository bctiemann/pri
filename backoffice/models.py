from encrypted_fields import fields

from django.db import models

from fleet.models import VehicleMarketing, VehicleType, VehicleStatus


# vehicles
# class Vehicle(models.Model):
#
#     # Fields defined on the model correspond to database columns and fully define their behavior both in DB and in code.
#     # Model field names should be verbose, specific, and expressive; i.e. "vehicle_type" rather than "vtype"
#     # Note that an auto-incrementing integer "id" field is implicit in all models, unless overridden using the
#     # "primary_key" parameter on a custom defined field
#     # https://docs.djangoproject.com/en/3.1/ref/models/fields/
#     make = models.CharField(max_length=255, blank=True)
#     model = models.CharField(max_length=255, blank=True)
#     year = models.IntegerField(null=True, blank=True)
#     vehicle_type = models.CharField(choices=VehicleType.choices, max_length=20, blank=True)
#     status = models.IntegerField(choices=VehicleStatus.choices, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     acquired_on = models.DateField(null=True, blank=True)
#     relinquished_on = models.DateField(null=True, blank=True)
#     plate = models.CharField(max_length=10, blank=True)
#     vin = models.CharField(max_length=50, blank=True)
#     mileage = models.IntegerField(null=True, blank=True)
#     damage = models.TextField(blank=True)
#     notes = models.TextField(blank=True)
#     policy_number = fields.EncryptedCharField(max_length=255, blank=True)
#     policy_company = models.CharField(max_length=255, blank=True)
#     policy_phone = models.CharField(max_length=30, blank=True)
#     weighting = models.IntegerField(null=True, blank=True)
#     redirect_to = models.ForeignKey('backoffice.Vehicle', null=True, blank=True, on_delete=models.SET_NULL)
#
#     # Example of a model property which produces a derived value (requires no params other than self), and thus is
#     # referenced as a property rather than being invoked as a method (with parentheses) - vehicle.vehicle_name
#     @property
#     def vehicle_name(self):
#         return f'{self.year} {self.make} {self.model}'
#
#     @property
#     def vehicle_marketing(self):
#         return VehicleMarketing.objects.filter(vehicle_id=self.id).first()
#
#     # This is the string representation of the vehicle object; will be used in the admin, templates, etc. as a default
#     def __str__(self):
#         return f'[{self.id}] {self.vehicle_name}'
#
#     # Meta subclass is used for defining attributes like default ordering
#     class Meta:
#         ordering = ('year',)
#

# class Service(models.Model):
#     pass
#
#
# class Damage(models.Model):
#     pass
#
#
# class TollTag(models.Model):
#     pass
#
#
# # sales
# # customer management
# class Customer(models.Model):
#     pass
#
#
# class Reservation(models.Model):
#     pass
#
#
# class Rental(models.Model):
#     pass
#
#
# class GuidedDrive(models.Model):
#     pass
#
#
# class GiftCertificate(models.Model):
#     pass
#
#
# class DiscountCode(models.Model):
#     pass
#
#
# class AdHocPayment(models.Model):
#     pass
#
#
# class SurveyResult(models.Model):
#     pass
#
#
# class Ban(models.Model):
#     pass
#
#
# # marketing
# class MassEmail(models.Model):
#     pass
#
#
# class News(models.Model):
#     pass
#
#
# class SiteContent(models.Model):
#     pass
#
#
# class NewsletterSubscription(models.Model):
#     pass
#
#
# # administration
# class Employee(models.Model):
#     pass
#
#
# class BBSPost(models.Model):
#     pass
#
#
# class SecurityLog(models.Model):
#     pass
