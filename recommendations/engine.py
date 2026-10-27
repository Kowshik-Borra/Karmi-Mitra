import math
from workers.models import Worker, WORKER_CATEGORIES

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth in kilometers (Haversine formula).
    """
    if None in (lat1, lon1, lat2, lon2):
        return 5.0  # default 5km fallback
    try:
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
        R = 6371.0  # Earth radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 2)
    except Exception:
        return 5.0


def rank_workers_for_request(
    category=None,
    skill_keyword=None,
    cust_lat=20.2961,
    cust_lon=85.8245,
    max_distance_km=25.0,
    target_budget=None,
    min_rating=0.0,
    min_experience=0,
    weights=None
):
    """
    Intelligent Recommendation Scoring Engine.
    Weights:
      skill_match: 25%
      rating: 20%
      distance: 20%
      availability: 15%
      experience: 10%
      price: 5%
      review_quality: 5%
    """
    if weights is None:
        weights = {
            'skill': 0.25,
            'rating': 0.20,
            'distance': 0.20,
            'availability': 0.15,
            'experience': 0.10,
            'price': 0.05,
            'review_quality': 0.05
        }

    queryset = Worker.objects.filter(is_verified=True)

    if category:
        queryset = queryset.filter(category__iexact=category)

    if min_rating > 0:
        queryset = queryset.filter(rating__gte=min_rating)

    if min_experience > 0:
        queryset = queryset.filter(years_of_experience__gte=min_experience)

    ranked_results = []

    for worker in queryset:
        # 1. Skill Match Score (0 - 100)
        skill_score = 100.0
        if skill_keyword and worker.skill_type:
            if skill_keyword.lower() in worker.skill_type.lower():
                skill_score = 100.0
            else:
                skill_score = 60.0

        # 2. Rating Score (0 - 100)
        rating_score = (float(worker.rating) / 5.0) * 100.0 if worker.rating else 70.0

        # 3. Distance Score (0 - 100)
        dist_km = calculate_haversine_distance(cust_lat, cust_lon, worker.latitude, worker.longitude)
        if dist_km > max_distance_km:
            continue  # Filter out workers beyond max distance
        dist_score = max(0.0, 100.0 - (dist_km / max_distance_km) * 100.0)

        # 4. Availability Score (0 - 100)
        avail_score = 100.0 if worker.availability == 'Yes' else 20.0

        # 5. Experience Score (0 - 100)
        exp_years = worker.years_of_experience or 0
        exp_score = min(100.0, (exp_years / 15.0) * 100.0)

        # 6. Price Score (0 - 100)
        price_score = 80.0
        if target_budget and worker.hourly_rate:
            target_budget = float(target_budget)
            h_rate = float(worker.hourly_rate)
            diff = abs(h_rate - target_budget)
            price_score = max(0.0, 100.0 - (diff / target_budget) * 100.0)

        # 7. Review Quality / Volume Score (0 - 100)
        review_count = worker.feedbacks.count()
        review_score = min(100.0, review_count * 20.0)

        # Calculate Total Weighted Score
        total_score = (
            weights['skill'] * skill_score +
            weights['rating'] * rating_score +
            weights['distance'] * dist_score +
            weights['availability'] * avail_score +
            weights['experience'] * exp_score +
            weights['price'] * price_score +
            weights['review_quality'] * review_score
        )

        ranked_results.append({
            'worker': worker,
            'distance_km': dist_km,
            'match_score': round(total_score, 1),
            'reasons': [
                f"Rating: {worker.rating}⭐",
                f"Distance: {dist_km} km",
                f"Experience: {worker.years_of_experience} yrs",
                "High skill match" if skill_score >= 90 else "Suitable category match",
                "Available now" if worker.availability == 'Yes' else "Limited availability"
            ]
        })

    # Sort descending by match score
    ranked_results.sort(key=lambda x: x['match_score'], reverse=True)
    return ranked_results


def classify_problem_description(text):
    """
    Natural Language Problem Classifier.
    Maps customer issue descriptions to service categories, urgency, and estimated cost range.
    """
    text_lower = text.lower()

    keywords_mapping = {
        'Plumber': ['leak', 'pipe', 'water', 'sink', 'tap', 'toilet', 'drain', 'flush', 'basin'],
        'Electrician': ['wire', 'spark', 'switch', 'light', 'short circuit', 'fuse', 'power', 'fan', 'appliance', 'mcb'],
        'Carpenter': ['wood', 'door', 'lock', 'table', 'chair', 'furniture', 'cabinet', 'hinge', 'wardrobe'],
        'Painter': ['paint', 'color', 'wall', 'stain', 'texture', 'waterproof', 'wallpaper'],
        'Housekeeping': ['clean', 'dust', 'mop', 'sanitiz', 'sweep', 'vacuum', 'deep clean'],
        'Mason': ['brick', 'cement', 'wall build', 'concrete', 'plaster', 'foundation'],
        'Tiles work': ['tile', 'marble', 'flooring', 'grout', 'granite'],
        'Cook or chef': ['cook', 'food', 'meal', 'kitchen', 'catering'],
        'Pest control service': ['pest', 'termite', 'cockroach', 'ant', 'bug', 'rat', 'rodent'],
        'CCTV technician': ['cctv', 'camera', 'security', 'dvr'],
    }

    detected_category = 'Other'
    matched_count = 0

    for cat, keywords in keywords_mapping.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > matched_count:
            matched_count = count
            detected_category = cat

    # Urgency analysis
    urgency = 'Medium'
    if any(word in text_lower for word in ['emergency', 'urgent', 'immediately', 'burst', 'fire', 'shock', 'overflowing']):
        urgency = 'High'
    elif any(word in text_lower for word in ['later', 'weekend', 'whenever', 'normal', 'quote']):
        urgency = 'Low'

    # Cost estimation based on category
    cost_estimates = {
        'Plumber': (400, 800),
        'Electrician': (350, 750),
        'Carpenter': (500, 1200),
        'Painter': (1000, 3000),
        'Housekeeping': (600, 1500),
        'Mason': (800, 2000),
        'Tiles work': (700, 1800),
        'Cook or chef': (500, 1200),
        'Pest control service': (900, 2500),
        'CCTV technician': (600, 1500),
        'Other': (400, 1000)
    }

    price_range = cost_estimates.get(detected_category, (400, 1000))

    return {
        'category': detected_category,
        'urgency': urgency,
        'estimated_cost_min': price_range[0],
        'estimated_cost_max': price_range[1],
        'summary': f"Identified as {detected_category} service ({urgency} priority)."
    }
