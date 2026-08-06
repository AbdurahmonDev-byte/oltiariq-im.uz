from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

# SITEMAP IMPORTLARI
from main.sitemaps import StaticViewSitemap, NewsSitemap, StudentSitemap, TeacherSitemap

# ADMIN: BARCHA MA'LUMOTLARNI O'CHIRISH TUGMASI
from main.admin_views import clear_all_data

sitemaps = {
    'static': StaticViewSitemap,
    'news': NewsSitemap,
    'students': StudentSitemap,
    'teachers': TeacherSitemap,
}

urlpatterns = [
    path('admin/clear-data/', clear_all_data, name='admin_clear_data'),
    path('admin/', admin.site.urls),
    path('rosetta/', include('rosetta.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

urlpatterns += i18n_patterns(
    path('', include('main.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)