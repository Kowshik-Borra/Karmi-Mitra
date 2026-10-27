from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'worker', 'customer_name', 'customer_contact', 'status', 'otp', 'otp_verified', 'booking_date')
    list_filter = ('status', 'otp_verified', 'booking_date')
    search_fields = ('customer_name', 'customer_contact', 'customer_email', 'worker__name', 'work_details')
    ordering = ('-booking_date',)
    actions = ['mark_completed', 'mark_confirmed']

    @admin.action(description='Mark selected bookings as Completed')
    def mark_completed(self, request, queryset):
        for booking in queryset:
            booking.status = 'Completed'
            booking.otp_verified = True
            booking.save()
            booking.worker.update_availability_status()

    @admin.action(description='Mark selected bookings as Confirmed')
    def mark_confirmed(self, request, queryset):
        queryset.update(status='Confirmed')
