from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import CustomerProfile
from workers.models import Worker, WORKER_CATEGORIES

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    customer_profile_id = serializers.SerializerMethodField()
    worker_profile_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'customer_profile_id', 'worker_profile_id', 'is_staff']

    def get_role(self, obj):
        if obj.is_staff or obj.is_superuser:
            return 'ADMIN'
        if hasattr(obj, 'worker_profile') and obj.worker_profile:
            return 'WORKER'
        if hasattr(obj, 'customer_profile') and obj.customer_profile:
            return 'CUSTOMER'
        return 'USER'

    def get_customer_profile_id(self, obj):
        if hasattr(obj, 'customer_profile') and obj.customer_profile:
            return obj.customer_profile.id
        return None

    def get_worker_profile_id(self, obj):
        if hasattr(obj, 'worker_profile') and obj.worker_profile:
            return obj.worker_profile.id
        return None


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'phone_no', 'address', 'latitude', 'longitude', 'avatar', 'created_at']


class RegisterCustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    phone_no = serializers.CharField(max_length=15)
    address = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, default=20.2961)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, default=85.8245)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone_no', 'address', 'latitude', 'longitude']

    def create(self, validated_data):
        phone_no = validated_data.pop('phone_no', '')
        address = validated_data.pop('address', '')
        latitude = validated_data.pop('latitude', 20.2961)
        longitude = validated_data.pop('longitude', 85.8245)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        CustomerProfile.objects.create(
            user=user,
            phone_no=phone_no,
            address=address,
            latitude=latitude,
            longitude=longitude
        )
        return user


class RegisterWorkerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    category = serializers.ChoiceField(choices=WORKER_CATEGORIES)
    age = serializers.IntegerField(default=25)
    gender = serializers.CharField(default='Male')
    contact_number = serializers.CharField(max_length=15)
    city_name = serializers.CharField(max_length=100)
    skill_type = serializers.CharField(max_length=150)
    experience_level = serializers.CharField(default='Intermediate')
    years_of_experience = serializers.IntegerField(default=3)
    hourly_rate = serializers.DecimalField(max_digits=8, decimal_places=2, default=500.00)
    price_min = serializers.DecimalField(max_digits=8, decimal_places=2, default=400.00)
    price_max = serializers.DecimalField(max_digits=8, decimal_places=2, default=800.00)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, default=20.2961)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, default=85.8245)
    bio = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Worker
        fields = [
            'username', 'email', 'password', 'name', 'age', 'gender', 'category',
            'contact_number', 'city_name', 'skill_type', 'experience_level',
            'years_of_experience', 'hourly_rate', 'price_min', 'price_max',
            'latitude', 'longitude', 'bio'
        ]

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.get('email')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=validated_data.get('name', '').split()[0] if validated_data.get('name') else '',
        )
        worker = Worker.objects.create(
            user=user,
            **validated_data
        )
        return worker
