from django.db import models
from django.contrib.auth.models import User

WORKER_CATEGORIES = [
    ('Mason', 'Mason'),
    ('Tiles work', 'Tiles work'),
    ('Rod building', 'Rod building'),
    ('Painter', 'Painter'),
    ('Plumber', 'Plumber'),
    ('Welder', 'Welder'),
    ('Ceiling', 'Ceiling'),
    ('Carpenter', 'Carpenter'),
    ('Electrician', 'Electrician'),
    ('Slab cutting', 'Slab cutting'),
    ('JCB or excavator service', 'JCB or excavator service'),
    ('Housekeeping', 'Housekeeping'),
    ('Cook or chef', 'Cook or chef'),
    ('Pest control service', 'Pest control service'),
    ('Home shifting service', 'Home shifting service'),
    ('Baby/elderly care', 'Baby/elderly care'),
    ('Plantation', 'Plantation'),
    ('Tailor', 'Tailor'),
    ('CCTV technician', 'CCTV technician'),
    ('Other', 'Other'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

EXPERIENCE_LEVEL_CHOICES = [
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Expert', 'Expert'),
]

AVAILABILITY_CHOICES = [
    ('Yes', 'Yes'),
    ('No', 'No'),
]

DAY_CHOICES = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
]

class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='worker_profile')
    name = models.CharField(max_length=150, verbose_name="Full Name")
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    category = models.CharField(max_length=100, choices=WORKER_CATEGORIES)
    contact_number = models.CharField(max_length=15, verbose_name="Contact Number")
    email = models.EmailField(unique=True)
    city_name = models.CharField(max_length=100, verbose_name="City")
    skill_type = models.CharField(max_length=150, verbose_name="Skill Type")
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES)
    years_of_experience = models.PositiveIntegerField()
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=500.00, verbose_name="Hourly Rate (INR)")
    price_min = models.DecimalField(max_digits=8, decimal_places=2, default=400.00, verbose_name="Min Price (INR)")
    price_max = models.DecimalField(max_digits=8, decimal_places=2, default=800.00, verbose_name="Max Price (INR)")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=20.2961, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=85.8245, verbose_name="Longitude")
    bio = models.TextField(blank=True, null=True, verbose_name="Bio / About Worker")
    is_verified = models.BooleanField(default=True, verbose_name="Is Verified Worker")
    profile_image = models.ImageField(upload_to='uploads/', default='uploads/default.jpg', blank=True, null=True)
    availability = models.CharField(max_length=5, choices=AVAILABILITY_CHOICES, default='Yes')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Worker_info'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.category}) - {self.city_name}"

    def update_availability_status(self):
        """
        Update worker availability dynamically based on completed / active bookings.
        """
        completed_count = self.bookings.filter(status='Completed').count()
        if completed_count >= 10:
            self.availability = 'No'
        else:
            self.availability = 'Yes'
        self.save(update_fields=['availability'])


class WorkerAvailability(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField(default="09:00:00")
    end_time = models.TimeField(default="18:00:00")
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = 'Worker_availability'
        unique_together = ('worker', 'day_of_week')

    def __str__(self):
        day_name = dict(DAY_CHOICES).get(self.day_of_week, 'Unknown')
        return f"{self.worker.name} - {day_name} ({self.start_time} to {self.end_time})"

