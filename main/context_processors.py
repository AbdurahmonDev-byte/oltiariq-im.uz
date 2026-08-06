from django.conf import settings


def site_background(request):
    """Barcha sahifalar tepasidagi fon uchun rasm URL'ini beradi."""
    return {
        'BG_IMAGE_URL': getattr(settings, 'SITE_BG_IMAGE', ''),
        'SITE_URL': getattr(settings, 'SITE_URL', 'https://oltiariq-im.uz'),
    }
