import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Loyihaning asosiy yo'li
BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env():
    env_path = BASE_DIR / '.env'
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        os.environ.setdefault(key.strip(), value.strip())


_load_env()

# Xavfsizlik sozlamalari (qiymatlar .env faylidan o'qiladi)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-oltiariq-im-2026-super-key')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Saytning asosiy (kanonik) manzili — SEO/OG/sitemap uchun
SITE_URL = os.environ.get('SITE_URL', 'https://oltiariq-im.uz')

# Barcha sahifalar tepasidagi fon rasmi (media/site-bg.jpg kabi).
# Bo'sh bo'lsa faqat animatsion chiziqlar (Background Paths) ko'rinadi.
SITE_BG_IMAGE = os.environ.get('SITE_BG_IMAGE', '')

# Ruxsat etilgan hostlar (.env da ALLOWED_HOSTS vergul bilan beriladi)
_allowed_hosts = os.environ.get(
    'ALLOWED_HOSTS',
    'oltiariq-im.uz,www.oltiariq-im.uz,abdurahmonmaxsutaliyev.pythonanywhere.com,127.0.0.1,localhost'
)
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(',') if h.strip()]

# HTTPS/xavfsizlik (production). PythonAnywhere proksi ortida ishlaydi
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
else:
    SECURE_PROXY_SSL_HEADER = None
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
# Ilovalar ro'yxati
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main', # Sening asosiy ilovang
    'rosetta',
    'django.contrib.sitemaps', # Sitemaps uchun
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # KO'P TILLI TIZIM UCHUN SHART
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Agar tashqarida templates bo'lsa
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n', # Til uchun
                'main.context_processors.site_background',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Ma'lumotlar bazasi (SQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Kesh (tezlik uchun) — in-memory, qisqa muddat
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'oltiariq-im',
        'TIMEOUT': 300,
    }
}

# Parol tekshiruvi
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# TIL VA VAQT SOZLAMALARI (2026-yil Abdurahmon Maxsutaliyev tahriri)
LANGUAGE_CODE = 'uz' # Asosiy til
TIME_ZONE = 'Asia/Tashkent' # O'zbekiston vaqti
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Qaysi tillar bo'lishi
LANGUAGES = [
    ('uz', _('O‘zbek')),
    ('en', _('English')),
    ('ru', _('Русский')),
]

# Tarjima fayllari qayerda turishi
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale/'),
]

# STATIC FAYLLAR (CSS, JS, Logo)
STATIC_URL = 'static/'
# Static fayllar main ichida bo'lgani uchun:
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'main/static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise orqali production'da statik fayllarni siqish/kesh
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

# MEDIA FAYLLAR (O'qituvchi, O'quvchi rasmlari va Sertifikatlar)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'