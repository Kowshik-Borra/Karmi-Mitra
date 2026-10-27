from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Worker, WorkerAvailability, WORKER_CATEGORIES
from .forms import WorkerRegistrationForm

# DRF Imports
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from workers.serializers import (
    WorkerListSerializer,
    WorkerDetailSerializer,
    WorkerAvailabilitySerializer
)
from recommendations.engine import calculate_haversine_distance

# -------------------------------------------------------------------
# DRF REST API VIEWS
# -------------------------------------------------------------------

class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all().order_by('-rating', '-created_at')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'me']:
            return WorkerDetailSerializer
        return WorkerListSerializer

    def update(self, request, *args, **kwargs):
        worker = self.get_object()
        if not (request.user.is_staff or request.user == worker.user):
            return Response({'error': 'You can only update your own profile.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        worker = self.get_object()
        if not (request.user.is_staff or request.user == worker.user):
            return Response({'error': 'You can only update your own profile.'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        if not hasattr(request.user, 'worker_profile') or not request.user.worker_profile:
            return Response({'error': 'User is not registered as a worker.'}, status=status.HTTP_404_NOT_FOUND)
        
        worker = request.user.worker_profile
        if request.method == 'GET':
            serializer = WorkerDetailSerializer(worker)
            return Response(serializer.data)
        
        serializer = WorkerDetailSerializer(worker, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search') or self.request.query_params.get('q')
        availability = self.request.query_params.get('availability')
        min_rating = self.request.query_params.get('min_rating')
        max_price = self.request.query_params.get('max_price')
        min_experience = self.request.query_params.get('min_experience')
        sort_by = self.request.query_params.get('sort_by')

        if category:
            qs = qs.filter(category__iexact=category)

        if availability:
            qs = qs.filter(availability__iexact=availability)

        if min_rating:
            try:
                qs = qs.filter(rating__gte=float(min_rating))
            except ValueError:
                pass

        if max_price:
            try:
                qs = qs.filter(hourly_rate__lte=float(max_price))
            except ValueError:
                pass

        if min_experience:
            try:
                qs = qs.filter(years_of_experience__gte=int(min_experience))
            except ValueError:
                pass

        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(category__icontains=search) |
                Q(city_name__icontains=search) |
                Q(skill_type__icontains=search)
            )

        if sort_by == 'rating_desc':
            qs = qs.order_by('-rating')
        elif sort_by == 'price_asc':
            qs = qs.order_by('hourly_rate')
        elif sort_by == 'experience_desc':
            qs = qs.order_by('-years_of_experience')

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Calculate distances if customer coordinates are provided
        cust_lat = request.query_params.get('lat')
        cust_lon = request.query_params.get('lon')

        page = self.paginate_queryset(queryset)
        workers_list = page if page is not None else queryset

        data = []
        for worker in workers_list:
            serializer_data = WorkerListSerializer(worker).data
            if cust_lat and cust_lon:
                serializer_data['distance_km'] = calculate_haversine_distance(
                    cust_lat, cust_lon, worker.latitude, worker.longitude
                )
            else:
                serializer_data['distance_km'] = 2.5
            data.append(serializer_data)

        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_status(self, request, pk=None):
        worker = self.get_object()
        if request.user.is_staff or (request.user == worker.user):
            worker.availability = 'No' if worker.availability == 'Yes' else 'Yes'
            worker.save(update_fields=['availability'])
            return Response({'status': 'success', 'availability': worker.availability})
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)



class WorkerAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = WorkerAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'worker_profile') and user.worker_profile:
            return WorkerAvailability.objects.filter(worker=user.worker_profile)
        return WorkerAvailability.objects.none()

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'worker_profile'):
            serializer.save(worker=self.request.user.worker_profile)


# -------------------------------------------------------------------
# LEGACY TEMPLATE VIEWS
# -------------------------------------------------------------------

def index(request):
    """
    Main Karmi Mitra Homepage with service categories & search
    """
    category_query = request.GET.get('category', '')
    search_query = request.GET.get('q', '')

    workers = Worker.objects.all()

    if category_query:
        workers = workers.filter(category__iexact=category_query)

    if search_query:
        workers = workers.filter(
            Q(city_name__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(skill_type__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    categories_list = [c[0] for c in WORKER_CATEGORIES]

    return render(request, 'index.html', {
        'workers': workers,
        'selected_category': category_query,
        'search_query': search_query,
        'categories_list': categories_list,
    })

def worker_list(request):
    """
    Worker directory listing page
    """
    category = request.GET.get('category', '')
    city_search = request.GET.get('search', '')

    workers = Worker.objects.all()

    if category:
        workers = workers.filter(category__iexact=category)

    if city_search:
        workers = workers.filter(city_name__icontains=city_search)

    return render(request, 'workers/worker_list.html', {
        'workers': workers,
        'category': category,
        'city_search': city_search,
        'worker_count': workers.count()
    })

def worker_detail(request, pk):
    """
    Detailed page for a specific worker
    """
    worker = get_object_or_404(Worker, pk=pk)
    feedbacks = worker.feedbacks.all()
    return render(request, 'workers/worker_detail.html', {
        'worker': worker,
        'feedbacks': feedbacks
    })

def worker_register(request):
    """
    Worker Registration Form handling
    """
    if request.method == 'POST':
        form = WorkerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            worker = form.save()
            messages.success(request, f"Registration successful! Welcome {worker.name}.")
            return redirect('workers:worker_detail', pk=worker.pk)
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = WorkerRegistrationForm()

    return render(request, 'workers/worker_register.html', {'form': form})

def toggle_availability(request, pk):
    """
    Toggle worker availability status ('Yes' / 'No')
    """
    worker = get_object_or_404(Worker, pk=pk)
    worker.availability = 'No' if worker.availability == 'Yes' else 'Yes'
    worker.save(update_fields=['availability'])
    messages.success(request, f"Updated availability status for {worker.name} to {worker.availability}.")
    return redirect('workers:worker_detail', pk=worker.pk)
