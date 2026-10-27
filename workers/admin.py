from django.contrib import admin
from .models import Worker

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'city_name', 'contact_number', 'availability', 'rating', 'created_at')
    list_filter = ('category', 'availability', 'experience_level', 'gender', 'city_name')
    search_fields = ('name', 'email', 'contact_number', 'city_name', 'skill_type')
    ordering = ('-created_at',)
    actions = ['make_available', 'make_unavailable']

    @admin.action(description='Mark selected workers as Available (Yes)')
    def make_available(self, request, queryset):
        queryset.update(availability='Yes')

    @admin.action(description='Mark selected workers as Unavailable (No)')
    def make_unavailable(self, request, queryset):
        queryset.update(availability='No')
