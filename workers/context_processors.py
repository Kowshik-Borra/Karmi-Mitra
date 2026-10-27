from .models import WORKER_CATEGORIES

def categories_processor(request):
    """
    Makes WORKER_CATEGORIES list available in all templates.
    """
    categories = [cat[0] for cat in WORKER_CATEGORIES]
    return {
        'all_categories': categories,
    }
