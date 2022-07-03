from django.utils import timezone


def get_year(request):
    return {
        'year': timezone.now().year
    }
