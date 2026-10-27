from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('worker', 'customer_name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('customer_name', 'worker__name', 'comments')
    ordering = ('-created_at',)
