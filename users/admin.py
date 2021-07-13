from django.contrib import admin

from users.models import User, Customer, MusicGenre


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email',)
    readonly_fields = ('created_by', 'last_login',)
    search_fields = ('email',)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'user',)
    autocomplete_fields = ('user',)
    readonly_fields = ('registration_ip', 'registration_lat', 'registration_long',)
    fieldsets = (
        (None, {
            'fields': ('user', 'first_name', 'last_name', 'id_old',)
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
            'fields': ('rentals_count', 'remarks', 'driver_skill', 'discount', 'music_genre',)
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
admin.site.register(Customer, CustomerAdmin)
admin.site.register(MusicGenre, MusicGenreAdmin)
