import random
import requests
from localflavor.us.models import USStateField, USZipCodeField, USSocialSecurityNumberField
from phonenumber_field.modelfields import PhoneNumberField
from encrypted_fields import fields
from english_words import english_words_lower_set

from django.conf import settings
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from users.enums import AdminIdleTimeCSSClass


def generate_password():
    words = [w for w in english_words_lower_set if len(w) < 8 and len(w) > 3]
    digit_string = random.randrange(100, 1000)
    return f'{random.choice(words).capitalize()}{digit_string}{random.choice(words).capitalize()}'


class LowercaseEmailField(models.EmailField):
    """
    Override EmailField to convert emails to lowercase before saving.
    """
    def to_python(self, value):
        """
        Convert email to lowercase.
        """
        value = super(LowercaseEmailField, self).to_python(value)
        # Value can be None so check that it's a string before lowercasing.
        if isinstance(value, str):
            return value.lower()
        return value


class EncryptedUSSocialSecurityNumberField(fields.EncryptedFieldMixin, USSocialSecurityNumberField):
    pass


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


# User is based on the internal Django authentication model, used for all password logins
class User(PermissionsMixin, AbstractBaseUser):
    email = LowercaseEmailField(
        verbose_name='email address',
        max_length=191,
        unique=True,
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be allowed to login. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_admin = models.BooleanField(default=False, help_text='Designates whether this user has access to the admin site.')
    is_backoffice = models.BooleanField(default=False, help_text='Designates whether this user has access to the backoffice site.')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL)
    last_login = models.DateTimeField(null=True, blank=True)
    admin_last_activity = models.DateTimeField(null=True, blank=True)
    id_orig = models.IntegerField(null=True, blank=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    # def has_perm(self, perm, obj=None):
    #     "Does the user have a specific permission?"
    #     # Simplest possible answer: Yes, always
    #     return True

    # def has_module_perms(self, app_label):
    #     "Does the user have permissions to view the app `app_label`?"
    #     # Simplest possible answer: Yes, always
    #     return True

    def set_password(self, raw_password):
        self.date_password_changed = timezone.now()
        super().set_password(raw_password)

    @property
    def is_staff(self):
        # Is the user a member of staff?
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def is_sleeping(self):
        if not self.admin_last_activity:
            return None
        return (timezone.now() - self.admin_last_activity).total_seconds() > settings.ADMIN_SLEEP_TIMEOUT_SECS

    @property
    def last_activity_css_class(self):
        if not self.admin_last_activity:
            return None
        last_activity_age_secs = (timezone.now() - self.admin_last_activity).total_seconds()
        if last_activity_age_secs < 3600:
            return AdminIdleTimeCSSClass.LESS_THAN_1_HOUR.value
        if last_activity_age_secs < 86400 * 2:
            return AdminIdleTimeCSSClass.LESS_THAN_2_DAYS.value
        return AdminIdleTimeCSSClass.MORE_THAN_2_DAYS.value

    @property
    def full_name(self):
        try:
            return f'{self.customer.first_name} {self.customer.last_name}'
        except Customer.DoesNotExist:
            try:
                return f'{self.employee.first_name} {self.employee.last_name}'
            except Employee.DoesNotExist:
                return self.email


class Employee(models.Model):

    class Status(models.IntegerChoices):
        EMPLOYED = (1, 'Employed')
        SUSPENDED = (2, 'Suspended')
        FIRED = (3, 'Fired')
        QUIT = (4, 'Quit')

    class EmploymentType(models.IntegerChoices):
        CONTRACTOR = (1, '1099')
        FULLTIME = (2, 'Fulltime')
        CORP = (3, 'Corp')

    class AccessLevel(models.IntegerChoices):
        ADMIN = (1, 'Admin')
        RESERVATIONS = (2, 'Reservations')
        MAINTENANCE = (3, 'Maintenance')
        MARKETING = (4, 'Marketing')
        BBS = (5, 'BBS Only')

    user = models.OneToOneField('users.User', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)

    # Mailing address, license, and ssn are encrypted
    address_line_1 = fields.EncryptedCharField(max_length=255)
    address_line_2 = fields.EncryptedCharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    state = USStateField()
    zip = USZipCodeField()
    work_phone = PhoneNumberField(blank=True)
    mobile_phone = PhoneNumberField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    ssn = EncryptedUSSocialSecurityNumberField(null=True, blank=True)
    license_number = fields.EncryptedCharField(max_length=30, blank=True)
    license_state = USStateField(blank=True)

    # Employment details
    hired_on = models.DateField(null=True, blank=True)
    status = models.IntegerField(choices=Status.choices, blank=True, default=Status.EMPLOYED)
    position = models.CharField(max_length=100, blank=True)
    employment_type = models.IntegerField(choices=EmploymentType.choices, default=EmploymentType.FULLTIME)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    access_level = models.IntegerField(choices=AccessLevel.choices, default=AccessLevel.BBS)
    rfid = fields.EncryptedCharField(max_length=255, blank=True)
    notes = fields.EncryptedTextField(blank=True)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def reservations_access(self):
        return self.access_level in (self.AccessLevel.ADMIN, self.AccessLevel.RESERVATIONS)

    @property
    def maintenance_access(self):
        return self.access_level in (self.AccessLevel.ADMIN, self.AccessLevel.MAINTENANCE)

    @property
    def marketing_access(self):
        return self.access_level in (self.AccessLevel.ADMIN, self.AccessLevel.MARKETING)

    @property
    def admin_access(self):
        return self.access_level == self.AccessLevel.ADMIN

    @property
    def any_privileged_access(self):
        return self.access_level != self.AccessLevel.BBS

    def __str__(self):
        return f'[{self.id}] {self.first_name} {self.last_name}'


# Customer contains all business data for a customer, and optionally is linked to a login user
class Customer(models.Model):

    class DriversClubLevel(models.IntegerChoices):
        NO = (0, 'No')
        SILVER = (1, 'Silver')
        GOLD = (2, 'Gold')
        PLATINUM = (3, 'Platinum')

    user = models.OneToOneField('users.User', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)

    # Mailing address lines are encrypted
    address_line_1 = fields.EncryptedCharField(max_length=255)
    address_line_2 = fields.EncryptedCharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    state = USStateField()
    zip = USZipCodeField()

    # Use home_phone.as_national to display in (555) 123-1234 style
    home_phone = PhoneNumberField(blank=True)
    work_phone = PhoneNumberField(blank=True)
    mobile_phone = PhoneNumberField(blank=True)
    fax = PhoneNumberField(blank=True)

    date_of_birth = models.DateField(null=True, blank=True)

    license_number = fields.EncryptedCharField(max_length=30, blank=True)
    license_state = USStateField(blank=True)
    license_history = fields.EncryptedTextField(blank=True)

    insurance_company = models.CharField(max_length=255, blank=True)
    insurance_policy_number = fields.EncryptedCharField(max_length=255, blank=True)
    insurance_company_phone = PhoneNumberField(blank=True)
    coverage_verified = models.BooleanField(default=False)

    cc_number = fields.EncryptedCharField(max_length=255, blank=True, verbose_name='CC1 number')
    cc_exp_yr = models.CharField(max_length=4, blank=True, verbose_name='CC1 exp year')
    cc_exp_mo = models.CharField(max_length=2, blank=True, verbose_name='CC1 exp month')
    cc_cvv = models.CharField(max_length=6, blank=True, verbose_name='CC1 CVV')
    cc_phone = PhoneNumberField(blank=True, verbose_name='CC1 contact phone')

    cc2_number = fields.EncryptedCharField(max_length=255, blank=True, verbose_name='CC2 number')
    cc2_exp_yr = models.CharField(max_length=4, blank=True, verbose_name='CC2 exp year')
    cc2_exp_mo = models.CharField(max_length=2, blank=True, verbose_name='CC2 exp month')
    cc2_cvv = models.CharField(max_length=6, blank=True, verbose_name='CC2 CVV')
    cc2_phone = PhoneNumberField(blank=True, verbose_name='CC2 contact phone')

    rentals_count = models.IntegerField(null=True, blank=True)
    remarks = fields.EncryptedTextField(blank=True)
    rating = models.IntegerField(null=True, blank=True)
    driver_skill = models.IntegerField(null=True, blank=True)
    discount_pct = models.IntegerField(null=True, blank=True)
    music_genre = models.ForeignKey('users.MusicGenre', null=True, blank=True, on_delete=models.SET_NULL)
    music_favorite = models.CharField(max_length=255, blank=True)

    first_time = models.BooleanField(default=True)
    drivers_club = models.IntegerField(choices=DriversClubLevel.choices, null=True, blank=True)
    receive_email = models.BooleanField(default=True)
    ban = models.BooleanField(default=False)
    survey_done = models.BooleanField(default=False)

    registration_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='Registration IP')
    registration_long = models.FloatField(null=True, blank=True, verbose_name='Registration longitude')
    registration_lat = models.FloatField(null=True, blank=True, verbose_name='Registration latitude')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def ip_country(self):
        url = f'http://ip-api.com/json/{self.registration_ip}'
        response = requests.get(url)
        result = response.json()
        return result.get('country')

    @property
    def has_mappable_address(self):
        return bool(self.address_line_1 and self.zip)

    @property
    def mappable_address(self):
        return f'{self.address_line_1}, {self.zip}'

    def format_cc_number(self, cc_number):
        if len(cc_number) == 16:
            cc_number = cc_number[0:4] + ' ' + cc_number[4:8] + ' ' + cc_number[8:12] + ' ' + cc_number[12:16]
        elif len(cc_number) == 15:
            cc_number = cc_number[0:4] + ' ' + cc_number[4:10] + ' ' + cc_number[10:15]
        return cc_number

    def save(self, *args, **kwargs):
        self.cc_number = self.format_cc_number((self.cc_number))
        self.cc2_number = self.format_cc_number((self.cc2_number))
        super().save(*args, **kwargs)

    def __str__(self):
        return f'[{self.id}] {self.first_name} {self.last_name}'


class MusicGenre(models.Model):
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
