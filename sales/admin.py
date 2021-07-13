from django.contrib import admin

from sales.models import Reservation


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'customer',)


admin.site.register(Reservation, ReservationAdmin)
