from django.db import models

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True, null=True)
    icon_name = models.CharField(max_length=50, default="Wrench", help_text="Icon identifier for frontend rendering")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Service_category'
        verbose_name_plural = "Service Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class ServiceSkill(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=150, verbose_name="Skill Name")
    estimated_price_min = models.DecimalField(max_digits=8, decimal_places=2, default=300.00)
    estimated_price_max = models.DecimalField(max_digits=8, decimal_places=2, default=800.00)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Service_skill'
        unique_together = ('category', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"

