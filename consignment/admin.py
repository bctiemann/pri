from django.contrib import admin

from consignment.models import Consigner, ConsignmentPayment, ConsignmentReservation


class ConsignerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name',)


class ConsignmentPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'consigner', 'amount',)


class ConsignmentReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'consigner', 'vehicle', 'out_at', 'back_at',)


admin.site.register(Consigner, ConsignerAdmin)
admin.site.register(ConsignmentPayment, ConsignmentPaymentAdmin)
admin.site.register(ConsignmentReservation, ConsignmentReservationAdmin)
