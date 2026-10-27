import os
# pyrefly: ignore [missing-import]
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# pyrefly: ignore [missing-import]
from django.contrib.auth.models import User
from accounts.models import CustomerProfile
from workers.models import Worker, WorkerAvailability
from services.models import ServiceCategory, ServiceSkill
from bookings.models import Booking
from feedback.models import Feedback
from payments.models import Payment
from notifications.models import Notification

def setup():
    print("Seeding Karmi Mitra database with realistic sample data...")

    # 1. Admin Superuser
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@karmimitra.org',
            'first_name': 'System',
            'last_name': 'Admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print("  [SUCCESS] Superuser created: username='admin', password='admin123'")


    # 2. Service Categories & Skills
    categories_data = [
        {
            'name': 'Electrician',
            'slug': 'electrician',
            'icon_name': 'Zap',
            'description': 'Electrical wiring, MCB fixes, fan & light installation, appliance repair',
            'skills': ['House Wiring', 'Circuit Repair', 'Fan & AC Installation', 'Inverter Setup']
        },
        {
            'name': 'Plumber',
            'slug': 'plumber',
            'icon_name': 'Droplet',
            'description': 'Pipe leak repair, tap replacement, bathroom fitting, water tank cleaning',
            'skills': ['Leak Repairs', 'Bathroom Fitting', 'Water Pipe Installation', 'Drain Cleaning']
        },
        {
            'name': 'Carpenter',
            'slug': 'carpenter',
            'icon_name': 'Hammer',
            'description': 'Furniture repair, door locks, wooden cupboards, custom woodwork',
            'skills': ['Door Lock Repair', 'Modular Furniture', 'Wooden Repair', 'Custom Cabinets']
        },
        {
            'name': 'Painter',
            'slug': 'painter',
            'icon_name': 'Paintbrush',
            'description': 'Interior wall painting, texture finish, exterior coating, waterproofing',
            'skills': ['Interior Painting', 'Wall Texture', 'Waterproofing', 'Exterior Coating']
        },
        {
            'name': 'Mason',
            'slug': 'mason',
            'icon_name': 'Grid',
            'description': 'Brickwork, concrete plastering, boundary wall construction',
            'skills': ['Brickwork', 'Plastering', 'Concrete Foundation', 'Wall Repair']
        },
        {
            'name': 'Housekeeping',
            'slug': 'housekeeping',
            'icon_name': 'Sparkles',
            'description': 'Deep home sanitization, carpet cleaning, sofa shampooing',
            'skills': ['Deep House Cleaning', 'Kitchen Sanitization', 'Sofa & Carpet Wash', 'Disinfection']
        }
    ]

    for cat in categories_data:
        category_obj, _ = ServiceCategory.objects.get_or_create(
            name=cat['name'],
            defaults={
                'slug': cat['slug'],
                'icon_name': cat['icon_name'],
                'description': cat['description']
            }
        )
        for skill_name in cat['skills']:
            ServiceSkill.objects.get_or_create(
                category=category_obj,
                name=skill_name,
                defaults={'estimated_price_min': 400.00, 'estimated_price_max': 900.00}
            )

    # 3. Sample Customer User
    customer_user, created = User.objects.get_or_create(
        username='democustomer',
        defaults={
            'email': 'customer@karmimitra.org',
            'first_name': 'Ananya',
            'last_name': 'Mishra'
        }
    )
    if created:
        customer_user.set_password('customer123')
        customer_user.save()
        CustomerProfile.objects.create(
            user=customer_user,
            phone_no='9876500001',
            address='Plot 104, Saheed Nagar, Bhubaneswar',
            latitude=Decimal('20.2961'),
            longitude=Decimal('85.8245')
        )
        print("  [SUCCESS] Demo Customer created: username='democustomer', password='customer123'")

    # 4. Sample Workers & Worker Users
    sample_workers = [
        {
            'username': 'ramesh_mason',
            'name': 'Ramesh Kumar',
            'age': 34,
            'gender': 'Male',
            'category': 'Mason',
            'contact_number': '9876543210',
            'email': 'ramesh.mason@example.com',
            'city_name': 'Bhubaneswar',
            'skill_type': 'Building Masonry & Brickwork',
            'experience_level': 'Expert',
            'years_of_experience': 10,
            'hourly_rate': Decimal('600.00'),
            'price_min': Decimal('500.00'),
            'price_max': Decimal('1000.00'),
            'latitude': Decimal('20.2980'),
            'longitude': Decimal('85.8260'),
            'rating': Decimal('4.8'),
            'bio': 'Expert mason with 10 years experience in residential brickwork and wall plastering.'
        },
        {
            'username': 'priya_cleaner',
            'name': 'Priya Das',
            'age': 28,
            'gender': 'Female',
            'category': 'Housekeeping',
            'contact_number': '9876543211',
            'email': 'priya.cleaning@example.com',
            'city_name': 'Cuttack',
            'skill_type': 'Deep House Cleaning & Sanitization',
            'experience_level': 'Intermediate',
            'years_of_experience': 5,
            'hourly_rate': Decimal('450.00'),
            'price_min': Decimal('400.00'),
            'price_max': Decimal('800.00'),
            'latitude': Decimal('20.4625'),
            'longitude': Decimal('85.8828'),
            'rating': Decimal('4.6'),
            'bio': 'Punctual housekeeping specialist providing deep cleaning and sanitization services.'
        },
        {
            'username': 'suresh_electric',
            'name': 'Suresh Naik',
            'age': 40,
            'gender': 'Male',
            'category': 'Electrician',
            'contact_number': '9876543212',
            'email': 'suresh.electric@example.com',
            'city_name': 'Bhubaneswar',
            'skill_type': 'House Wiring & Circuit Repair',
            'experience_level': 'Expert',
            'years_of_experience': 12,
            'hourly_rate': Decimal('700.00'),
            'price_min': Decimal('500.00'),
            'price_max': Decimal('1200.00'),
            'latitude': Decimal('20.3010'),
            'longitude': Decimal('85.8190'),
            'rating': Decimal('4.9'),
            'bio': 'Certified electrician specializing in short circuit repairs, full house wiring, and MCB setups.'
        },
        {
            'username': 'amit_plumber',
            'name': 'Amit Mohanty',
            'age': 30,
            'gender': 'Male',
            'category': 'Plumber',
            'contact_number': '9876543213',
            'email': 'amit.plumber@example.com',
            'city_name': 'Puri',
            'skill_type': 'Pipe Fitting & Leak Repairs',
            'experience_level': 'Intermediate',
            'years_of_experience': 6,
            'hourly_rate': Decimal('500.00'),
            'price_min': Decimal('400.00'),
            'price_max': Decimal('900.00'),
            'latitude': Decimal('19.8135'),
            'longitude': Decimal('85.8312'),
            'rating': Decimal('4.5'),
            'bio': 'Reliable plumber available for pipe leaks, tap installs, and bathroom repairs.'
        },
        {
            'username': 'rajesh_painter',
            'name': 'Rajesh Patnaik',
            'age': 36,
            'gender': 'Male',
            'category': 'Painter',
            'contact_number': '9876543214',
            'email': 'rajesh.painter@example.com',
            'city_name': 'Bhubaneswar',
            'skill_type': 'Wall Painting & Texture',
            'experience_level': 'Expert',
            'years_of_experience': 8,
            'hourly_rate': Decimal('550.00'),
            'price_min': Decimal('500.00'),
            'price_max': Decimal('1100.00'),
            'latitude': Decimal('20.2910'),
            'longitude': Decimal('85.8210'),
            'rating': Decimal('4.7'),
            'bio': 'Creative painter providing smooth wall finishes, waterproofing, and modern texture art.'
        }
    ]

    for data in sample_workers:
        uname = data.pop('username')
        user, u_created = User.objects.get_or_create(
            username=uname,
            defaults={'email': data['email'], 'first_name': data['name'].split()[0]}
        )
        if u_created:
            user.set_password('worker123')
            user.save()

        worker, created = Worker.objects.get_or_create(
            email=data['email'],
            defaults={'user': user, **data}
        )
        if created:
            print(f"  [SUCCESS] Added worker: {worker.name} ({worker.category})")
            # Create availability schedule
            for day in range(7):
                WorkerAvailability.objects.create(
                    worker=worker,
                    day_of_week=day,
                    is_available=True if day != 6 else False  # Sunday off
                )

    # 5. Create Sample Booking & Feedback for Suresh Naik
    suresh = Worker.objects.get(email='suresh.electric@example.com')
    sample_booking, b_created = Booking.objects.get_or_create(
        customer=customer_user,
        worker=suresh,
        defaults={
            'customer_name': 'Ananya Mishra',
            'customer_age': 29,
            'customer_address': 'Plot 104, Saheed Nagar, Bhubaneswar',
            'customer_contact': '9876500001',
            'customer_email': 'customer@karmimitra.org',
            'work_details': 'Fix MCB tripping problem in main circuit box.',
            'status': 'Completed',
            'otp': '847291',
            'otp_verified': True,
            'estimated_amount': Decimal('750.00')
        }
    )

    if b_created:
        Payment.objects.create(
            booking=sample_booking,
            amount=Decimal('750.00'),
            payment_method='UPI',
            status='SUCCESS',
            transaction_id='TXN-DEMO12345'
        )
        Feedback.objects.create(
            worker=suresh,
            booking=sample_booking,
            customer_name='Ananya Mishra',
            rating=5,
            comments='Suresh arrived promptly and fixed the circuit box within 30 minutes! Highly recommended.'
        )
        Notification.objects.create(
            user=customer_user,
            title="Welcome to Karmi Mitra!",
            message="Your account is active. Find top local workers with our AI recommendation engine.",
            notification_type='SYSTEM'
        )
        print("  [SUCCESS] Sample booking, payment, and feedback created!")

    print("\nSeed data setup completed successfully!")


if __name__ == '__main__':
    setup()
