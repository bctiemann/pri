from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext, gettext_lazy as _

from users.models import User, Employee, Customer, MusicGenre


class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'customer', 'employee', 'is_admin', 'is_backoffice', 'last_login', 'is_sleeping', 'created_at',)
    readonly_fields = ('created_by', 'last_login',)
    search_fields = ('email',)
    list_filter = ('is_admin', 'is_backoffice',)
    ordering = ('-id',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {
            'fields': ('is_active', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'user', 'created_at',)
    search_fields = ('user__email', 'first_name', 'last_name',)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'user',)
    autocomplete_fields = ('user',)
    readonly_fields = ('registration_ip', 'registration_lat', 'registration_long',)
    search_fields = ('user__email', 'first_name', 'last_name',)
    fieldsets = (
        (None, {
            'fields': ('user', 'first_name', 'last_name',)
        }),
        ('Mailing address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'zip',)
        }),
        ('Phone numbers', {
            'fields': ('home_phone', 'work_phone', 'mobile_phone', 'fax',)
        }),
        ('License', {
            'fields': ('date_of_birth', 'license_number', 'license_state', 'license_history',)
        }),
        ('Credit Card 1', {
            'fields': ('cc_number', 'cc_exp_yr', 'cc_exp_mo', 'cc_cvv', 'cc_phone',)
        }),
        ('Credit Card 2', {
            'fields': ('cc2_number', 'cc2_exp_yr', 'cc2_exp_mo', 'cc2_cvv', 'cc2_phone',)
        }),
        ('Details', {
            'fields': ('rentals_count', 'remarks', 'driver_skill', 'discount_pct', 'music_genre',)
        }),
        ('Options', {
            'fields': ('first_time', 'drivers_club', 'no_email', 'ban', 'survey_done',)
        }),
        ('Registration', {
            'fields': ('registration_ip', 'registration_lat', 'registration_long',)
        })
    )


class MusicGenreAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(User, UserAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(MusicGenre, MusicGenreAdmin)
