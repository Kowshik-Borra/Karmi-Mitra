from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomerRegistrationForm, UserLoginForm
from .models import CustomerProfile
from bookings.models import Booking

# DRF Imports
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import (
    UserSerializer,
    CustomerProfileSerializer,
    RegisterCustomerSerializer,
    RegisterWorkerSerializer
)

# -------------------------------------------------------------------
# DRF REST API VIEWS
# -------------------------------------------------------------------

class RegisterCustomerAPIView(generics.CreateAPIView):
    serializer_class = RegisterCustomerSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Customer registered successfully.',
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class RegisterWorkerAPIView(generics.CreateAPIView):
    serializer_class = RegisterWorkerSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        worker = serializer.save()
        user = worker.user
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Worker registered successfully.',
            'user': UserSerializer(user).data,
            'worker_id': worker.id,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class UserProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserSerializer(user).data
        if hasattr(user, 'customer_profile') and user.customer_profile:
            data['customer_profile'] = CustomerProfileSerializer(user.customer_profile).data
        if hasattr(user, 'worker_profile') and user.worker_profile:
            from workers.serializers import WorkerDetailSerializer
            data['worker_profile'] = WorkerDetailSerializer(user.worker_profile).data
        return Response(data)

    def put(self, request):
        user = request.user
        first_name = request.data.get('first_name', user.first_name)
        last_name = request.data.get('last_name', user.last_name)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        if hasattr(user, 'customer_profile') and user.customer_profile:
            cp = user.customer_profile
            cp.phone_no = request.data.get('phone_no', cp.phone_no)
            cp.address = request.data.get('address', cp.address)
            cp.latitude = request.data.get('latitude', cp.latitude)
            cp.longitude = request.data.get('longitude', cp.longitude)
            cp.save()

        return Response({
            'message': 'Profile updated successfully.',
            'user': UserSerializer(user).data
        })


class AdminAnalyticsAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from workers.models import Worker
        from payments.models import Payment
        from django.db.models import Sum, Avg, Count

        total_users = User.objects.count()
        total_customers = CustomerProfile.objects.count()
        total_workers = Worker.objects.count()

        total_bookings = Booking.objects.count()
        completed_bookings = Booking.objects.filter(status='Completed').count()
        pending_bookings = Booking.objects.filter(status='Pending').count()
        cancelled_bookings = Booking.objects.filter(status='Cancelled').count()

        revenue_agg = Payment.objects.filter(status='SUCCESS').aggregate(Sum('amount'))['amount__sum'] or 0.0
        avg_rating_agg = Worker.objects.aggregate(Avg('rating'))['rating__avg'] or 0.0

        # Category distribution
        category_dist = Worker.objects.values('category').annotate(count=Count('id')).order_by('-count')

        # Recent Bookings
        recent_bookings = Booking.objects.select_related('worker').order_by('-booking_date')[:5]
        recent_data = [{
            'id': b.id,
            'customer_name': b.customer_name,
            'worker_name': b.worker.name,
            'status': b.status,
            'amount': b.estimated_amount,
            'date': b.booking_date.strftime('%Y-%m-%d %H:%M')
        } for b in recent_bookings]

        return Response({
            'total_users': total_users,
            'total_customers': total_customers,
            'total_workers': total_workers,
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'pending_bookings': pending_bookings,
            'cancelled_bookings': cancelled_bookings,
            'total_revenue': float(revenue_agg),
            'avg_rating': round(avg_rating_agg, 1),
            'category_distribution': list(category_dist),
            'recent_activity': recent_data
        })



# -------------------------------------------------------------------
# LEGACY TEMPLATE VIEWS
# -------------------------------------------------------------------

def register_user(request):
    """
    Handle Customer Registration
    """
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_no = form.cleaned_data['phone_no']
            password = form.cleaned_data['password']

            username = email.split('@')[0]
            if User.objects.filter(username=username).exists():
                username = f"{username}_{User.objects.count() + 1}"

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            CustomerProfile.objects.create(
                user=user,
                phone_no=phone_no
            )

            login(request, user)
            messages.success(request, "Registration successful! Welcome to Karmi Mitra.")
            return redirect('index')
        else:
            messages.error(request, "Registration failed. Please correct errors below.")
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_user(request):
    """
    Handle Customer/Worker Login
    """
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next') or 'index'
                return redirect(next_url)
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_user(request):
    """
    Handle User Logout
    """
    logout(request)
    messages.info(request, "You have logged out successfully.")
    return redirect('index')

@login_required
def profile_dashboard(request):
    """
    Customer Dashboard & Booking history
    """
    customer_bookings = Booking.objects.filter(customer=request.user)
    return render(request, 'accounts/profile.html', {
        'bookings': customer_bookings
    })
