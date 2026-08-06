from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap as django_sitemap

# SITEMAP IMPORTLARI
from main.sitemaps import StaticViewSitemap, NewsSitemap, StudentSitemap, TeacherSitemap, GraduateSitemap

# ADMIN: BARCHA MA'LUMOTLARNI O'CHIRISH TUGMASI
from main.admin_views import clear_all_data
from main.views import robots_txt

sitemaps = {
    'static': StaticViewSitemap,
    'news': NewsSitemap,
    'students': StudentSitemap,
    'teachers': TeacherSitemap,
    'graduates': GraduateSitemap,
}


def sitemap_view(request, *args, **kwargs):
    """Sitemap URL'lari har doim asosiy domenda (SITE_URL) va https'da bo'lishi uchun host/schemenni majburlaydi."""
    host = settings.SITE_URL.replace('https://', '').replace('http://', '').rstrip('/')
    request.META['HTTP_HOST'] = host
    request.META['SERVER_NAME'] = host.split(':')[0]
    if settings.SITE_URL.startswith('https://'):
        request.META['wsgi.url_scheme'] = 'https'
    return django_sitemap(request, *args, **kwargs)


urlpatterns = [
    path('admin/clear-data/', clear_all_data, name='admin_clear_data'),
    path('admin/', admin.site.urls),
    path('rosetta/', include('rosetta.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('sitemap.xml', sitemap_view, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
]

urlpatterns += i18n_patterns(
    path('', include('main.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)