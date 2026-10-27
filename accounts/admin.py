from django.contrib import admin
from .models import CustomerProfile

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_no', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone_no')
    ordering = ('-created_at',)
