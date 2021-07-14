from django.contrib import admin

from sales.models import Reservation, Discount


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'customer',)


class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'amount', 'percent',)


admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Discount, DiscountAdmin)