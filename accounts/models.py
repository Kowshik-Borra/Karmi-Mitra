from django.db import models
from django.contrib.auth.models import User

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_no = models.CharField(max_length=15, verbose_name="Phone Number")
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=20.2961, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=85.8245, verbose_name="Longitude")
    avatar = models.ImageField(upload_to='customers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Customer_info'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.phone_no})"

