from rest_framework import serializers
from services.models import ServiceCategory, ServiceSkill

class ServiceSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSkill
        fields = ['id', 'name', 'estimated_price_min', 'estimated_price_max', 'description']


class ServiceCategorySerializer(serializers.ModelSerializer):
    skills = ServiceSkillSerializer(many=True, read_only=True)
    worker_count = serializers.SerializerMethodField()

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'slug', 'description', 'icon_name', 'is_active', 'skills', 'worker_count']

    def get_worker_count(self, obj):
        from workers.models import Worker
        return Worker.objects.filter(category=obj.name).count()
