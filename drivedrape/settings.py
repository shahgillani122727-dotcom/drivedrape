import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-change-this-in-production-use-env-variable'

DEBUG = True  # Set to False in production

ALLOWED_HOSTS = ['*']  # Update with your domain in production

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    #'cloudinary',
    #'cloudinary_storage',
    # Local apps
    'core',
    'products',
    'cart',
    'orders',
    'accounts',
    'payments',
    'dashboard',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'drivedrape.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_count',  # Global cart count
            ],
        },
    },
]

WSGI_APPLICATION = 'drivedrape.wsgi.application'

# ─── DATABASE ───────────────────────────────────────────
# SQLite for development, PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# For production PostgreSQL, use:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME'),
#         'USER': os.environ.get('DB_USER'),
#         'PASSWORD': os.environ.get('DB_PASSWORD'),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True

# ─── STATIC & MEDIA ─────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─── CLOUDINARY (for production image hosting) ──────────
# CLOUDINARY_STORAGE = {
#     'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
#     'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
#     'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
# }
# DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── AUTH ────────────────────────────────────────────────
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'accounts.Customer'

# ─── SESSION ─────────────────────────────────────────────
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400 * 7  # 7 days

# ─── EMAIL ───────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = 'Drive Drape <your@gmail.com>'

# ─── WHATSAPP ────────────────────────────────────────────
WHATSAPP_BUSINESS_NUMBER = os.environ.get('WHATSAPP_NUMBER', '+923170004122')

# ─── JAZZCASH ────────────────────────────────────────────
JAZZCASH_MERCHANT_ID = os.environ.get('JAZZCASH_MERCHANT_ID', '')
JAZZCASH_PASSWORD = os.environ.get('JAZZCASH_PASSWORD', '')
JAZZCASH_INTEGRITY_SALT = os.environ.get('JAZZCASH_INTEGRITY_SALT', '')
JAZZCASH_SANDBOX = True  # Set False in production

# ─── EASYPAISA ───────────────────────────────────────────
EASYPAISA_STORE_ID = os.environ.get('EASYPAISA_STORE_ID', '')
EASYPAISA_HASH_KEY = os.environ.get('EASYPAISA_HASH_KEY', '')
