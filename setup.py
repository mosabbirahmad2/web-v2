import os
import sys
import subprocess

print("=" * 75)
print("🚀 Fantacy Tech: সম্পূর্ণ প্রজেক্ট প্রোডাকশন-গ্রেড সেটআপ ও সেল্ফ-হিলিং...")
print("=" * 75)

FILES = {}

# -------------------------------------------------------------
# 1. ROOT RUNTIME CONFIGURATIONS
# -------------------------------------------------------------
FILES["requirements.txt"] = """Django==5.0.6
Pillow>=9.5.0
python-dotenv>=1.0.0
whitenoise>=6.6.0
gunicorn>=21.2.0
dj-database-url>=2.1.0
django-ratelimit>=4.1.0
"""

FILES[".gitignore"] = """.env
db.sqlite3
__pycache__/
*.py[cod]
*$py.class
staticfiles/
media/
node_modules/
.DS_Store
"""

FILES[".env"] = """# ====================================================================
# ⚠️ WARNING: BEFORE DEPLOYING TO PRODUCTION:
# 1. Set DEBUG=False
# 2. Generate a secure random SECRET_KEY using:
#    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# 3. Set ALLOWED_HOSTS to your actual domain name(s)
# ====================================================================

DEBUG=True
SECRET_KEY=django-insecure-prod-ready-fantacy-tech-bangladesh-key-2026-xyz
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

ADMIN_LOCKOUT_MAX_ATTEMPTS=3
ADMIN_LOCKOUT_DURATION_MINUTES=720

# Optional PostgreSQL Database
# DATABASE_URL=postgres://user:password@localhost:5432/fantacytech_db

# Optional Redis Cache
# REDIS_URL=redis://127.0.0.1:6379/1
"""

FILES["Procfile"] = """web: gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
"""

FILES["package.json"] = """{
  "name": "fantacytech-tailwind",
  "version": "1.0.0",
  "description": "Tailwind CLI asset pipeline for Fantacy Tech",
  "scripts": {
    "build:css": "tailwindcss -i ./src/input.css -o ./static/css/app.css --minify",
    "watch:css": "tailwindcss -i ./src/input.css -o ./static/css/app.css --watch"
  },
  "devDependencies": {
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3"
  }
}
"""

FILES["tailwind.config.js"] = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./products/**/*.py",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
      },
      colors: {
        themeBrown: '#5C3214',
        zatiqPurple: '#541DFF',
      }
    },
  },
  plugins: [],
}
"""

FILES["src/input.css"] = """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer utilities {
  .cart-drawer {
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }
  .cart-hidden {
    transform: translateX(100%);
  }
}

@keyframes marquee {
  0% { transform: translateX(100%); }
  100% { transform: translateX(-100%); }
}

.animate-marquee {
  display: inline-block;
  white-space: nowrap;
  animation: marquee 25s linear infinite;
}
"""

FILES["static/css/app.css"] = """@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
*, ::before, ::after { box-sizing: border-box; border-width: 0; border-style: solid; border-color: #e2e8f0; }
html { line-height: 1.5; -webkit-text-size-adjust: 100%; font-family: 'Plus Jakarta Sans', sans-serif; }
body { margin: 0; line-height: inherit; }
.cart-drawer { transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.cart-hidden { transform: translateX(100%); }
@keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
.animate-marquee { display: inline-block; white-space: nowrap; animation: marquee 25s linear infinite; }
.btn-purple { background-color: #541DFF; color: white; }
.btn-purple:hover { background-color: #4313d6; }
.active-nav { background-color: #EDE9FE; color: #541DFF; font-weight: 700; }
"""

# -------------------------------------------------------------
# 2. SMART main.py & manage.py
# -------------------------------------------------------------
FILES["main.py"] = """import os
import sys
import subprocess

def ensure_manage_py():
    if not os.path.exists('manage.py'):
        with open('manage.py', 'w', encoding='utf-8') as f:
            f.write('''import os
import sys

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)
''')

def run_command(command):
    ensure_manage_py()
    full_cmd = [sys.executable, "manage.py"] + command.split()
    try:
        subprocess.run(full_cmd, check=True)
    except KeyboardInterrupt:
        print("\\nStopped by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ensure_manage_py()
    if len(sys.argv) == 1:
        try:
            print("Auto-checking database migrations...")
            subprocess.run([sys.executable, "manage.py", "migrate"])
            subprocess.run([sys.executable, "manage.py", "createcachetable"])
            subprocess.run([sys.executable, "manage.py", "runserver", "0.0.0.0:5000"])
        except KeyboardInterrupt:
            print("\\nServer stopped.")
    else:
        action = sys.argv[1]
        print(f"Executing: {action}...")
        run_command(f"{action} {' '.join(sys.argv[2:])}")
"""

FILES["manage.py"] = """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
"""

# -------------------------------------------------------------
# 3. CORE SETTINGS & ROUTING
# -------------------------------------------------------------
FILES["core/__init__.py"] = ""

FILES["core/asgi.py"] = """import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
application = get_asgi_application()
"""

FILES["core/wsgi.py"] = """import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
application = get_wsgi_application()
"""

FILES["core/urls.py"] = """from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from products.sitemaps import ProductSitemap, CategorySitemap
from products.views import robots_txt_view

admin.site.site_header = "Fantacy Tech Administration"
admin.site.site_title = "Fantacy Tech Portal"
admin.site.index_title = "Database Administration"

sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt_view, name='robots_txt'),
    path('', include('products.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.BASE_DIR / 'static')
"""

FILES["core/settings.py"] = """import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-fallback-key-strictly-for-local-development-only'
    else:
        raise RuntimeError("CRITICAL: SECRET_KEY is missing in production mode (DEBUG=False).")

allowed_hosts_raw = os.getenv('ALLOWED_HOSTS', '')
if not allowed_hosts_raw:
    ALLOWED_HOSTS = ['*'] if DEBUG else []
else:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_raw.split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'products.apps.ProductsConfig',
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
    'products.middleware.AnalyticsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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
                'django.template.context_processors.media',
                'products.context_processors.site_settings_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

import dj_database_url
database_url = os.getenv('DATABASE_URL')
if database_url:
    DATABASES = {
        'default': dj_database_url.config(default=database_url, conn_max_age=600, conn_health_checks=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

redis_url = os.getenv('REDIS_URL')
if redis_url:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': redis_url,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'django_shared_cache_table',
        }
    }

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = '/mosabbiradmin/login/'
LOGIN_REDIRECT_URL = '/mosabbiradmin/'
LOGOUT_REDIRECT_URL = '/mosabbiradmin/login/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_AGE = 1800

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
"""

# -------------------------------------------------------------
# 4. SITEMAPS & PRODUCTS MODELS
# -------------------------------------------------------------
FILES["products/sitemaps.py"] = """from django.contrib.sitemaps import Sitemap
from .models import Product, Category

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True).order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return obj.get_absolute_url()

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.filter(is_active=True).order_by('order', 'name')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
"""

FILES["products/__init__.py"] = ""

FILES["products/apps.py"] = """from django.apps import AppConfig
class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
"""

FILES["products/admin.py"] = """from django.contrib import admin
from .models import Category, Product, ProductImage, ProductReview, Order, OrderItem, PromoCode, SiteSetting, StoreVisitSession

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'name', 'category', 'price', 'discount_price', 'stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'product_code', 'description')

admin.site.register(ProductImage)
admin.site.register(ProductReview)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PromoCode)
admin.site.register(SiteSetting)
admin.site.register(StoreVisitSession)
"""

FILES["products/context_processors.py"] = """from django.core.cache import cache
from .models import SiteSetting, Category

def site_settings_processor(request):
    site_setting = cache.get('global_site_settings')
    if not site_setting:
        site_setting = SiteSetting.get_settings()
        cache.set('global_site_settings', site_setting, timeout=300)

    global_categories = cache.get('global_active_categories')
    if global_categories is None:
        global_categories = list(Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related('subcategories'))
        cache.set('global_active_categories', global_categories, timeout=300)

    return {
        'site_setting': site_setting,
        'global_categories': global_categories
    }
"""

FILES["products/middleware.py"] = """from .models import AnalyticsEvent, StoreVisitSession

BOT_USER_AGENTS = ('bot', 'crawl', 'spider', 'slurp', 'facebookexternalhit', 'whatsapp', 'curl', 'python-requests')

class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if (request.method == 'GET' and 
            not path.startswith('/static/') and 
            not path.startswith('/media/') and 
            not path.startswith('/django-admin/') and 
            not path.startswith('/mosabbiradmin/') and
            not path.startswith('/api/') and
            path not in ('/favicon.ico', '/robots.txt')):
            
            ua = request.META.get('HTTP_USER_AGENT', '')
            ua_lower = ua.lower()

            if not any(b in ua_lower for b in BOT_USER_AGENTS):
                ip = request.META.get('HTTP_X_FORWARDED_FOR')
                ip = ip.split(',')[0].strip() if ip else request.META.get('REMOTE_ADDR')

                if not request.session.session_key:
                    request.session.save()
                session_key = request.session.session_key

                if not request.session.get('visit_logged'):
                    request.session['visit_logged'] = True
                    try:
                        StoreVisitSession.objects.create(session_key=session_key, ip_address=ip)
                    except Exception:
                        pass

                device = 'Mobile' if any(w in ua_lower for w in ['mobile', 'android', 'iphone']) else 'Desktop'
                browser = 'Chrome' if 'chrome' in ua_lower and 'edg' not in ua_lower else ('Firefox' if 'firefox' in ua_lower else ('Safari' if 'safari' in ua_lower else 'Other'))

                try:
                    AnalyticsEvent.objects.create(
                        ip_address=ip,
                        user_agent=ua[:200],
                        device_type=device,
                        browser=browser,
                        path=path[:250],
                        event_type='visit',
                        referrer=request.META.get('HTTP_REFERER', '')[:250]
                    )
                except Exception:
                    pass

        return self.get_response(request)
"""

FILES["products/models.py"] = """import os
import uuid
from io import BytesIO
from PIL import Image

from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.cache import cache
from django.db.models import Avg
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

def optimize_image(image_field, max_size=(1000, 1000), quality=85):
    if not image_field or not hasattr(image_field, 'file'):
        return
    try:
        img = Image.open(image_field)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        out = BytesIO()
        img.save(out, format='WEBP', quality=quality, optimize=True)
        out.seek(0)
        
        base_name = os.path.basename(image_field.name)
        clean_name = os.path.splitext(base_name)[0]
        image_field.file = ContentFile(out.read())
        image_field.name = f"{clean_name}.webp"
    except Exception:
        pass


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=100, default="Fantacy Tech")
    contact_phone = models.CharField(max_length=30, default="01999999999")
    whatsapp_number = models.CharField(max_length=30, default="01999999999")
    whatsapp_username = models.CharField(max_length=100, default="fantacytech", blank=True)
    contact_email = models.EmailField(default="support@fantacytech.com")
    office_address = models.TextField(default="Dhaka, Bangladesh")
    announcement_notice = models.CharField(max_length=300, default="Welcome to Fantacy Tech! Premium Phone Covers & Key Rings with Fast Home Delivery!")
    delivery_fee_dhaka = models.DecimalField(max_digits=6, decimal_places=2, default=70.00)
    delivery_fee_outside = models.DecimalField(max_digits=6, decimal_places=2, default=130.00)
    theme_color = models.CharField(max_length=30, default="#5C3214")
    theme_mode = models.CharField(max_length=10, default="light", choices=(('light', 'Light'), ('dark', 'Dark')))
    enable_buy_now = models.BooleanField(default=True)

    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True, default="Fantacy Tech - Premium Mobile Covers & Accessories")
    meta_description = models.CharField(max_length=160, blank=True, default="Shop premium mobile cases, custom key rings and luxury accessories online in Bangladesh with Cash on Delivery!")
    meta_keywords = models.CharField(max_length=255, blank=True, default="phone covers, mobile case, key rings, accessories, bangladesh, online shop")

    def __str__(self):
        return f"{self.site_name} Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete('global_site_settings')

    @classmethod
    def get_settings(cls):
        setting, _ = cls.objects.get_or_create(pk=1)
        return setting


class AdminLoginAttempt(models.Model):
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=150, default="admin")
    failed_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('ip_address', 'username')

    def is_locked(self):
        return bool(self.locked_until and self.locked_until > timezone.now())


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    short_description = models.TextField(blank=True, null=True)
    banner = models.ImageField(upload_to='categories/banners/', blank=True, null=True)
    image = models.ImageField(upload_to='categories/images/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def get_absolute_url(self):
        return f"/category/{self.slug}/"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "cat"
            slug = base
            c = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{c}"
                c += 1
            self.slug = slug
        if self.image and not getattr(self.image, '_committed', True):
            optimize_image(self.image, max_size=(600, 600))
        if self.banner and not getattr(self.banner, '_committed', True):
            optimize_image(self.banner, max_size=(1400, 450))
        super().save(*args, **kwargs)
        cache.delete('global_active_categories')

    def delete(self, *args, **kwargs):
        if self.image:
            try:
                self.image.delete(save=False)
            except Exception:
                pass
        if self.banner:
            try:
                self.banner.delete(save=False)
            except Exception:
                pass
        super().delete(*args, **kwargs)
        cache.delete('global_active_categories')

    def __str__(self):
        return f"{self.parent.name} > {self.name}" if self.parent else self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    product_code = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Product Code / SKU")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=50)
    badge_tag = models.CharField(max_length=50, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    def get_absolute_url(self):
        return f"/product/{self.pk}/"

    def clean(self):
        if self.discount_price and self.discount_price > self.price:
            raise ValidationError({'discount_price': 'Discount price cannot exceed regular price.'})

    def save(self, *args, **kwargs):
        if not self.product_code:
            code = f"FT-{uuid.uuid4().hex[:6].upper()}"
            while Product.objects.filter(product_code=code).exclude(pk=self.pk).exists():
                code = f"FT-{uuid.uuid4().hex[:6].upper()}"
            self.product_code = code

        if self.discount_price and self.discount_price > self.price:
            self.discount_price = self.price
        if not self.slug:
            base = slugify(self.name) or "prod"
            slug = base
            c = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{c}"
                c += 1
            self.slug = slug
        if self.image and not getattr(self.image, '_committed', True):
            optimize_image(self.image, max_size=(900, 900))
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for image_obj in self.images.all():
            if image_obj.image:
                try:
                    image_obj.image.delete(save=False)
                except Exception:
                    pass
            image_obj.delete()
        if self.image:
            try:
                self.image.delete(save=False)
            except Exception:
                pass
        super().delete(*args, **kwargs)

    @property
    def effective_price(self):
        if self.discount_price and self.discount_price > 0:
            return min(self.price, self.discount_price)
        return self.price

    @property
    def discount_percent(self):
        if self.discount_price and self.discount_price < self.price:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def avg_rating(self):
        avg = self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None

    @property
    def reviews_count(self):
        return self.reviews.filter(is_approved=True).count()

    def __str__(self):
        return f"[{self.product_code or 'NO-SKU'}] {self.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image and not getattr(self.image, '_committed', True):
            optimize_image(self.image, max_size=(900, 900))
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            try:
                self.image.delete(save=False)
            except Exception:
                pass
        super().delete(*args, **kwargs)


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer_name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ShowcaseSection(models.Model):
    STYLE_CHOICES = (
        ('light', 'White / Minimal'),
        ('brown', 'Warm Coffee Brown'),
        ('dark', 'Charcoal Black'),
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    background_style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='light')
    has_countdown = models.BooleanField(default=False)
    end_time = models.DateTimeField(null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True, related_name='showcases')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def is_expired(self):
        return bool(self.has_countdown and self.end_time and self.end_time <= timezone.now())

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "section"
            slug = base
            c = 1
            while ShowcaseSection.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{c}"
                c += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PromoCode(models.Model):
    DISCOUNT_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.PositiveIntegerField(default=10)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self, subtotal=0):
        if not self.is_active:
            return False, "This promo code is disabled."
        if self.expiry_date and self.expiry_date < timezone.now().date():
            return False, "This promo code has expired."
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False, "This promo code usage limit has been reached."
        if self.min_purchase and subtotal < self.min_purchase:
            return False, f"Minimum spend of ৳{self.min_purchase} required."
        return True, "Valid"

    def calculate_discount(self, subtotal):
        if self.discount_type == 'percentage':
            d = (subtotal * self.discount_value) / 100
            if self.max_discount and d > self.max_discount:
                d = self.max_discount
        else:
            d = self.discount_value
        return min(d, subtotal)

    def __str__(self):
        return self.code


class Order(models.Model):
    STATUS_CHOICES = (
        ('Placed', 'Placed'),
        ('On Hold', 'On Hold'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
    )
    order_id = models.CharField(max_length=32, unique=True, editable=False)
    customer_name = models.CharField(max_length=120)
    customer_phone = models.CharField(max_length=25)
    customer_email = models.EmailField(blank=True, null=True)
    delivery_zone = models.CharField(max_length=50, default="Inside Dhaka")
    district = models.CharField(max_length=80, default="Dhaka")
    thana = models.CharField(max_length=80, blank=True, null=True)
    shipping_address = models.TextField()
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=70.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='Placed', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            while True:
                candidate = f"FT-{uuid.uuid4().hex[:10].upper()}"
                if not Order.objects.filter(order_id=candidate).exists():
                    self.order_id = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255, blank=True)
    product_code = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.product:
            if not self.product_name:
                self.product_name = self.product.name
            if not self.product_code and self.product.product_code:
                self.product_code = self.product.product_code
        super().save(*args, **kwargs)


class UniqueVisitorLog(models.Model):
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ip_address', 'date')
        ordering = ['-created_at']


class StoreVisitSession(models.Model):
    session_key = models.CharField(max_length=100, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


class AnalyticsEvent(models.Model):
    EVENT_TYPES = (
        ('visit', 'Unique Visit'),
        ('product_view', 'Product View'),
        ('add_to_cart', 'Add to Cart'),
        ('checkout_start', 'Checkout Started'),
        ('order_completed', 'Order Completed'),
        ('search', 'Search Query'),
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default='')
    device_type = models.CharField(max_length=30, blank=True, default='Desktop')
    browser = models.CharField(max_length=40, blank=True, default='Chrome')
    referrer = models.CharField(max_length=255, blank=True, default='')
    path = models.CharField(max_length=255)
    event_type = models.CharField(max_length=40, choices=EVENT_TYPES, default='visit', db_index=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)


class SearchQuery(models.Model):
    query = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


@receiver(pre_delete, sender=Product)
def auto_delete_product_files(sender, instance, **kwargs):
    for image_obj in instance.images.all():
        if image_obj.image:
            try:
                image_obj.image.delete(save=False)
            except Exception:
                pass
        image_obj.delete()
    if instance.image:
        try:
            instance.image.delete(save=False)
        except Exception:
            pass
    instance.analyticsevent_set.all().delete()


@receiver(pre_save, sender=Product)
def auto_delete_old_product_image_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_file = Product.objects.get(pk=instance.pk).image
    except Product.DoesNotExist:
        return
    if old_file and old_file != instance.image:
        try:
            old_file.delete(save=False)
        except Exception:
            pass


@receiver(pre_delete, sender=ProductImage)
def auto_delete_product_image_file(sender, instance, **kwargs):
    if instance.image:
        try:
            instance.image.delete(save=False)
        except Exception:
            pass


@receiver(pre_delete, sender=Category)
def auto_delete_category_files(sender, instance, **kwargs):
    if instance.image:
        try:
            instance.image.delete(save=False)
        except Exception:
            pass
    if instance.banner:
        try:
            instance.banner.delete(save=False)
        except Exception:
            pass


@receiver(pre_save, sender=Category)
def auto_delete_old_category_files_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_cat = Category.objects.get(pk=instance.pk)
    except Category.DoesNotExist:
        return
    if old_cat.image and old_cat.image != instance.image:
        try:
            old_cat.image.delete(save=False)
        except Exception:
            pass
    if old_cat.banner and old_cat.banner != instance.banner:
        try:
            old_cat.banner.delete(save=False)
        except Exception:
            pass
"""

# -------------------------------------------------------------
# 5. MIGRATIONS
# -------------------------------------------------------------
FILES["products/migrations/0015_promocode_limits_and_indexes.py"] = """# Generated by Django 5.0.6
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0014_adminloginattempt_username_analyticsevent_browser_and_more'),
    ]
    operations = [
        migrations.AddField(
            model_name='promocode',
            name='usage_limit',
            field=models.PositiveIntegerField(blank=True, help_text='Maximum total usage limit', null=True),
        ),
        migrations.AddField(
            model_name='promocode',
            name='used_count',
            field=models.PositiveIntegerField(default=0, help_text='Number of times redeemed'),
        ),
        migrations.AlterField(
            model_name='analyticsevent',
            name='event_type',
            field=models.CharField(choices=[('visit', 'Unique Visit'), ('product_view', 'Product View'), ('add_to_cart', 'Add to Cart'), ('checkout_start', 'Checkout Started'), ('order_completed', 'Order Completed'), ('search', 'Search Query')], db_index=True, default='visit', max_length=40),
        ),
        migrations.AlterField(
            model_name='analyticsevent',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Placed', 'Placed'), ('On Hold', 'On Hold'), ('Confirmed', 'Confirmed'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned')], db_index=True, default='Placed', max_length=25),
        ),
    ]
"""

FILES["products/migrations/0016_product_product_code_orderitem_product_code.py"] = """# Generated by Django 5.0.6
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0015_promocode_limits_and_indexes'),
    ]
    operations = [
        migrations.AddField(
            model_name='product',
            name='product_code',
            field=models.CharField(blank=True, help_text='Product Code / SKU', max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
"""

FILES["products/migrations/0017_storevisitsession.py"] = """# Generated by Django 5.0.6
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0016_product_product_code_orderitem_product_code'),
    ]
    operations = [
        migrations.CreateModel(
            name='StoreVisitSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(db_index=True, max_length=100)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
        ),
    ]
"""

FILES["products/migrations/0018_seo_fields.py"] = """# Generated by Django 5.0.6
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0017_storevisitsession'),
    ]
    operations = [
        migrations.AddField(
            model_name='category',
            name='meta_description',
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_keywords',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_title',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_description',
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_keywords',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_title',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='meta_description',
            field=models.CharField(blank=True, default='Shop premium mobile cases, custom key rings and luxury accessories online in Bangladesh with Cash on Delivery!', max_length=160),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='meta_keywords',
            field=models.CharField(blank=True, default='phone covers, mobile case, key rings, accessories, bangladesh, online shop', max_length=255),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='meta_title',
            field=models.CharField(blank=True, default='Fantacy Tech - Premium Mobile Covers & Accessories', max_length=200),
        ),
    ]
"""

# -------------------------------------------------------------
# 6. MERCHANT TEMPLATES (CATEGORIES & CATEGORY DETAIL WITH FULL SEO)
# -------------------------------------------------------------
FILES["templates/merchant/categories.html"] = """{% extends 'merchant/base_merchant.html' %}
{% block title %}Categories - Merchant Panel{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto space-y-6">
  <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
    <h1 class="text-xl font-bold text-slate-800">Categories</h1>
    
    <div class="flex items-center gap-3 w-full sm:w-auto">
      <form method="GET" class="relative flex-1 sm:w-64">
        <input type="text" name="q" value="{{ search_query|default:'' }}" placeholder="Search" class="w-full border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-xs focus:outline-none focus:border-purple-600 bg-slate-50/50">
        <i class="fa-solid fa-magnifying-glass absolute left-3 top-2.5 text-slate-400 text-xs"></i>
      </form>
      <button onclick="openCreateCategoryModal()" class="px-4 py-2 bg-[#541DFF] hover:bg-[#4513db] text-white text-xs font-semibold rounded-lg flex items-center gap-2 shadow-sm transition whitespace-nowrap">
        <i class="fa-solid fa-plus text-xs"></i> Add Categories
      </button>
    </div>
  </div>

  <div class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
    <table class="w-full text-left text-xs text-slate-600 border-collapse">
      <thead class="bg-slate-50/70 border-b border-slate-200 text-slate-500 uppercase text-[10px] font-bold tracking-wider">
        <tr>
          <th class="p-4 w-12 text-center"></th>
          <th class="p-4">Categories</th>
          <th class="p-4 text-center">Total Subcategory</th>
          <th class="p-4 text-right"></th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
        {% for cat in categories %}
        <tr class="hover:bg-slate-50/60 transition group">
          <td class="p-4 text-center text-slate-300 group-hover:text-slate-500 cursor-grab">
            <i class="fa-solid fa-grip-vertical"></i>
          </td>
          <td class="p-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center overflow-hidden shrink-0">
                {% if cat.image %}
                  <img src="{{ cat.image.url }}" alt="{{ cat.name }}" class="w-full h-full object-cover">
                {% else %}
                  <i class="fa-regular fa-image text-slate-400 text-base"></i>
                {% endif %}
              </div>
              <div class="flex items-center gap-2">
                <a href="{% url 'merchant_category_detail' cat.pk %}" class="font-semibold text-slate-800 text-sm hover:text-[#541DFF] transition">
                  {{ cat.name }}
                </a>
                <a href="{% url 'shop_category' cat.slug %}" target="_blank" title="View live in shop" class="text-slate-300 hover:text-slate-600">
                  <i class="fa-solid fa-arrow-up-right-from-square text-[11px]"></i>
                </a>
              </div>
            </div>
          </td>
          <td class="p-4 text-center font-semibold text-slate-700">
            {{ cat.subcategories.count }}
          </td>
          <td class="p-4 text-right space-x-3 text-slate-400 whitespace-nowrap">
            <form method="POST" action="{% url 'merchant_toggle_category' cat.pk %}" class="inline">
              {% csrf_token %}
              <button type="submit" title="Toggle Visibility" class="hover:text-purple-600 p-1">
                <i class="fa-solid fa-eye {% if cat.is_active %}text-[#541DFF]{% else %}text-slate-300{% endif %}"></i>
              </button>
            </form>
            <a href="{% url 'merchant_category_detail' cat.pk %}" title="Edit Category" class="hover:text-purple-600 p-1 inline-block">
              <i class="fa-solid fa-pen text-xs"></i>
            </a>
            <button type="button" onclick="triggerActionModal('{% url 'merchant_delete_category' cat.pk %}', 'Are you sure you want to delete category {{ cat.name|escapejs }}?')" title="Delete Category" class="hover:text-rose-600 p-1 inline-block">
              <i class="fa-regular fa-trash-can text-xs"></i>
            </button>
          </td>
        </tr>
        {% empty %}
        <tr>
          <td colspan="4" class="p-16 text-center text-slate-400">
            <i class="fa-regular fa-folder-open text-3xl mb-2 text-slate-300 block"></i>
            No categories created yet. Click <strong>"+ Add Categories"</strong> above.
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>

<!-- Modal: Create Category -->
<div id="createCategoryModal" class="hidden fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
  <div class="bg-white rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl max-h-[92vh] overflow-y-auto">
    <div class="px-6 py-4 flex justify-between items-center border-b border-slate-100">
      <h3 class="text-base font-bold text-slate-900">Create Category</h3>
      <button type="button" onclick="closeCreateCategoryModal()" class="text-slate-400 hover:text-slate-700 text-2xl font-light leading-none">&times;</button>
    </div>

    <form method="POST" action="{% url 'merchant_categories' %}" enctype="multipart/form-data" class="p-6 space-y-5">
      {% csrf_token %}

      <div>
        <label class="block text-xs font-bold text-slate-700 mb-1.5">Banner/Cover</label>
        <div class="border-2 border-dashed border-slate-200 rounded-xl p-5 text-center bg-slate-50/50 hover:bg-slate-50/80 transition relative min-h-[150px] flex flex-col items-center justify-center">
          <div id="bannerPreviewContainer" class="hidden w-full mb-3">
            <img id="bannerPreviewImage" src="" alt="Banner Preview" class="h-28 w-full object-cover rounded-lg border border-slate-200 shadow-sm">
          </div>
          <div id="bannerPlaceholder" class="space-y-1.5">
            <div class="w-10 h-10 rounded-xl bg-purple-50 text-[#541DFF] flex items-center justify-center mx-auto text-lg mb-2">
              <i class="fa-regular fa-image"></i>
            </div>
            <p class="text-[11px] text-slate-500 max-w-md mx-auto leading-relaxed">
              Upload a banner image for the category. Recommended size is 1300×380 pixels. Maximum file size is 4MB.
            </p>
          </div>
          <input type="file" id="modal_cat_banner" name="banner" accept="image/*" class="hidden" onchange="openCropper(this, 1300/380, 'bannerPreviewImage', 'bannerPreviewContainer', 'bannerPlaceholder')">
          <button type="button" onclick="document.getElementById('modal_cat_banner').click()" class="mt-2 px-4 py-1.5 bg-purple-50 hover:bg-purple-100 text-[#541DFF] text-xs font-semibold rounded-lg transition">
            Add Image
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 items-start">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1.5">Image</label>
          <div class="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center bg-slate-50/50 hover:bg-slate-50/80 transition min-h-[250px] flex flex-col items-center justify-center">
            <div id="imagePreviewContainer" class="hidden mb-2">
              <img id="imagePreviewImage" src="" alt="Category Preview" class="w-24 h-24 object-cover rounded-xl border border-slate-200 shadow-sm">
            </div>
            <div id="imagePlaceholder" class="space-y-1.5 px-2">
              <div class="w-10 h-10 rounded-xl bg-purple-50 text-[#541DFF] flex items-center justify-center mx-auto text-lg mb-2">
                <i class="fa-regular fa-image"></i>
              </div>
              <p class="text-[10.5px] text-slate-500 leading-relaxed">
                Upload a square image for the category (1:1) aspect ratio. Recommended size is 500×500 pixels. Maximum file size is 4MB.
              </p>
            </div>
            <input type="file" id="modal_cat_image" name="image" accept="image/*" class="hidden" onchange="openCropper(this, 1, 'imagePreviewImage', 'imagePreviewContainer', 'imagePlaceholder')">
            <button type="button" onclick="document.getElementById('modal_cat_image').click()" class="mt-2 px-4 py-1.5 bg-purple-50 hover:bg-purple-100 text-[#541DFF] text-xs font-semibold rounded-lg transition">
              Add Image
            </button>
          </div>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1.5">Category Name <span class="text-rose-500">*</span></label>
            <input type="text" name="name" id="modalCatName" maxlength="50" required placeholder="Category Name" oninput="document.getElementById('nameCharCount').innerText = 50 - this.value.length" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs bg-slate-50/40 focus:bg-white focus:outline-none focus:border-[#541DFF] transition">
            <div class="text-right text-[10px] text-slate-400 mt-1">Character limit: <span id="nameCharCount">50</span></div>
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1.5">Short Description</label>
            <textarea name="short_description" rows="5" placeholder="Short description..." class="w-full border border-slate-200 rounded-xl p-3 text-xs bg-slate-50/40 focus:bg-white focus:outline-none focus:border-[#541DFF] transition"></textarea>
          </div>
        </div>
      </div>

      <!-- SEO Fields directly embedded -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 border-t pt-3">
        <div>
          <label class="block text-[11px] font-bold text-slate-600 mb-1">SEO Meta Title</label>
          <input type="text" name="meta_title" placeholder="Optional Category Title" class="w-full border rounded-xl px-3 py-1.5 text-xs bg-slate-50 outline-none">
        </div>
        <div>
          <label class="block text-[11px] font-bold text-slate-600 mb-1">SEO Description</label>
          <input type="text" name="meta_description" maxlength="160" placeholder="Optional snippet" class="w-full border rounded-xl px-3 py-1.5 text-xs bg-slate-50 outline-none">
        </div>
        <div>
          <label class="block text-[11px] font-bold text-slate-600 mb-1">SEO Keywords</label>
          <input type="text" name="meta_keywords" placeholder="category, collection" class="w-full border rounded-xl px-3 py-1.5 text-xs bg-slate-50 outline-none">
        </div>
      </div>

      <div class="flex gap-3 pt-4 border-t border-slate-100">
        <button type="button" onclick="closeCreateCategoryModal()" class="flex-1 py-2.5 border border-slate-200 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-50 transition">
          Cancel
        </button>
        <button type="submit" class="flex-1 py-2.5 bg-[#541DFF] hover:bg-[#4313d6] text-white rounded-xl text-xs font-bold shadow-md transition">
          Create
        </button>
      </div>
    </form>
  </div>
</div>

<script>
  function openCreateCategoryModal() { document.getElementById('createCategoryModal').classList.remove('hidden'); }
  function closeCreateCategoryModal() { document.getElementById('createCategoryModal').classList.add('hidden'); }
</script>
{% endblock %}
"""

FILES["templates/merchant/category_detail.html"] = """{% extends 'merchant/base_merchant.html' %}
{% block title %}Categories > {{ category.name }}{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto space-y-6">
  <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
    <div class="flex items-center gap-3">
      <a href="{% url 'merchant_categories' %}" class="w-8 h-8 rounded-full border border-slate-200 bg-white flex items-center justify-center text-slate-600 hover:bg-slate-50 transition shadow-sm">
        <i class="fa-solid fa-arrow-left text-xs"></i>
      </a>
      <div class="text-sm font-semibold text-slate-600 flex items-center gap-2">
        <a href="{% url 'merchant_categories' %}" class="hover:text-slate-900 transition">Categories</a>
        <span>&gt;</span>
        <span class="font-bold text-slate-900">{{ category.name }}</span>
      </div>
    </div>

    <button onclick="openSubCategoryModal()" class="px-4 py-2 bg-[#541DFF] hover:bg-[#4313d6] text-white text-xs font-semibold rounded-lg flex items-center gap-2 shadow-sm transition">
      <i class="fa-solid fa-plus text-xs"></i> Add Sub Categories
    </button>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
    <div class="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
      <form method="POST" enctype="multipart/form-data" class="space-y-5">
        {% csrf_token %}
        <input type="hidden" name="action" value="update_category">

        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1.5">Banner/Cover</label>
          <div class="border-2 border-dashed border-slate-200 rounded-xl p-5 text-center bg-slate-50/50 hover:bg-slate-50/80 transition relative min-h-[150px] flex flex-col items-center justify-center">
            <div id="detailBannerContainer" class="{% if not category.banner %}hidden{% endif %} w-full mb-3">
              <img id="detailBannerImage" src="{% if category.banner %}{{ category.banner.url }}{% endif %}" class="h-28 w-full object-cover rounded-lg border">
            </div>
            <div id="detailBannerPlaceholder" class="{% if category.banner %}hidden{% endif %}">
              <i class="fa-regular fa-image text-2xl text-slate-300 mb-1"></i>
            </div>
            <input type="file" id="detail_banner_input" name="banner" accept="image/*" class="hidden" onchange="openCropper(this, 1300/380, 'detailBannerImage', 'detailBannerContainer', 'detailBannerPlaceholder')">
            <button type="button" onclick="document.getElementById('detail_banner_input').click()" class="mt-1 px-4 py-1.5 bg-purple-50 text-[#541DFF] text-xs font-semibold rounded-lg">
              {% if category.banner %}Change Image{% else %}Add Image{% endif %}
            </button>
          </div>
          <p class="text-[10px] text-slate-400 mt-1 italic">Recommended size is 1300×380 pixels. Max file size: 4MB.</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5 items-start">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1.5">Image (1:1)</label>
            <div class="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center bg-slate-50/50 min-h-[220px] flex flex-col items-center justify-center">
              <div id="detailImageContainer" class="{% if not category.image %}hidden{% endif %} mb-2">
                <img id="detailImagePreview" src="{% if category.image %}{{ category.image.url }}{% endif %}" class="w-24 h-24 object-cover rounded-xl border">
              </div>
              <div id="detailImagePlaceholder" class="{% if category.image %}hidden{% endif %}">
                <i class="fa-regular fa-image text-2xl text-slate-300 mb-1"></i>
              </div>
              <input type="file" id="detail_image_input" name="image" accept="image/*" class="hidden" onchange="openCropper(this, 1, 'detailImagePreview', 'detailImageContainer', 'detailImagePlaceholder')">
              <button type="button" onclick="document.getElementById('detail_image_input').click()" class="mt-1 px-4 py-1.5 bg-purple-50 text-[#541DFF] text-xs font-semibold rounded-lg">
                {% if category.image %}Change Image{% else %}Add Image{% endif %}
              </button>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1.5">Category Name *</label>
              <input type="text" name="name" value="{{ category.name }}" maxlength="50" required oninput="document.getElementById('detailCharCount').innerText = 50 - this.value.length" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs bg-slate-50/40">
              <div class="text-right text-[10px] text-slate-400 mt-1">Character limit: <span id="detailCharCount">50</span></div>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1.5">Short Description</label>
              <textarea name="short_description" rows="5" class="w-full border border-slate-200 rounded-xl p-3 text-xs bg-slate-50/40">{{ category.short_description|default:'' }}</textarea>
            </div>
          </div>
        </div>

        <!-- SEO Fields directly embedded -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 border-t pt-3">
          <div>
            <label class="block text-[11px] font-bold text-slate-600 mb-1">SEO Meta Title</label>
            <input type="text" name="meta_title" value="{{ category.meta_title|default:'' }}" placeholder="Google title" class="w-full border rounded-xl px-3 py-1.5 text-xs bg-slate-50 outline-none">
          </div>
          <div>
            <label class="block text-[11px] font-bold text-slate-600 mb-1">SEO Description</label>
            <input type="text" name="meta_description" value="{{ category.meta_description|default:'' }}" maxlength="160" placeholder="Meta snippet" class="w-full border rounded-xl px-3 py-1.5 text-xs bg-slate-50 outline-none">
          </div>
          <div>
            <label class="block text-[11px] font-bold text-slate-600 mb-1">SEO Keywords</label>
            <input type="text" name="meta_keywords" value="{{ category.meta_keywords|default:'' }}" placeholder="tags" class="w-full border rounded-xl px-3 py-1.5 text-xs bg-slate-50 outline-none">
          </div>
        </div>

        <button type="submit" class="w-full py-3 bg-[#541DFF] hover:bg-[#4313d6] text-white rounded-xl text-xs font-bold shadow-md transition">
          Update Category
        </button>
      </form>
    </div>

    <!-- Right Column: Subcategories List -->
    <div class="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm min-h-[460px] flex flex-col justify-center">
      {% if subcategories %}
        <div class="w-full space-y-3">
          <h3 class="font-bold text-slate-800 text-xs uppercase tracking-wider mb-2">Sub Categories ({{ subcategories.count }})</h3>
          <div class="divide-y divide-slate-100">
            {% for sub in subcategories %}
            <div class="py-3 flex items-center justify-between group">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-slate-100 border overflow-hidden flex items-center justify-center shrink-0">
                  {% if sub.image %}<img src="{{ sub.image.url }}" class="w-full h-full object-cover">
                  {% else %}<i class="fa-solid fa-shapes text-slate-300"></i>{% endif %}
                </div>
                <div>
                  <h4 class="text-xs font-bold text-slate-800">{{ sub.name }}</h4>
                  <span class="text-[10px] text-slate-400">{{ sub.created_at|date:"M d, Y" }}</span>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button type="button" onclick="openEditSubModal('{{ sub.pk }}', '{{ sub.name|escapejs }}', '{{ sub.short_description|escapejs }}')" class="text-slate-400 hover:text-purple-600 p-1" title="Edit subcategory">
                  <i class="fa-solid fa-pen text-xs"></i>
                </button>
                <button type="button" onclick="triggerActionModal('{% url 'merchant_delete_category' sub.pk %}', 'Delete sub-category {{ sub.name|escapejs }}?')" class="text-slate-300 hover:text-rose-600 p-1">
                  <i class="fa-regular fa-trash-can text-xs"></i>
                </button>
              </div>
            </div>
            {% endfor %}
          </div>
        </div>
      {% else %}
        <div class="text-center space-y-3 py-10">
          <div class="w-16 h-16 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto text-2xl">
            <i class="fa-solid fa-box-open"></i>
          </div>
          <div class="space-y-1">
            <h4 class="text-sm font-bold text-slate-800">Your sub categories list is currently empty</h4>
            <p class="text-xs text-slate-400">Lets get started by adding your first sub category now</p>
          </div>
          <button type="button" onclick="openSubCategoryModal()" class="mt-2 px-5 py-2.5 bg-[#541DFF] hover:bg-[#4313d6] text-white text-xs font-semibold rounded-xl shadow-md transition">
            Add Sub Category
          </button>
        </div>
      {% endif %}
    </div>
  </div>
</div>

<!-- Modal: Create / Edit sub-category -->
<div id="createSubCategoryModal" class="hidden fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
  <div class="bg-white rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl max-h-[92vh] overflow-y-auto">
    <div class="px-6 py-4 flex justify-between items-center border-b border-slate-100">
      <h3 id="subModalTitle" class="text-base font-bold text-slate-900">Create sub-category</h3>
      <button type="button" onclick="closeSubCategoryModal()" class="text-slate-400 hover:text-slate-700 text-2xl font-light">&times;</button>
    </div>

    <form method="POST" action="{% url 'merchant_category_detail' category.pk %}" enctype="multipart/form-data" class="p-6 space-y-5">
      {% csrf_token %}
      <input type="hidden" name="action" id="sub_form_action" value="create_subcategory">
      <input type="hidden" name="sub_pk" id="sub_pk_field" value="">

      <div>
        <label class="block text-xs font-bold text-slate-700 mb-1.5">Banner/Cover</label>
        <div class="border-2 border-dashed border-slate-200 rounded-xl p-5 text-center bg-slate-50/50 min-h-[150px] flex flex-col items-center justify-center">
          <div id="subBannerPreviewContainer" class="hidden w-full mb-3">
            <img id="subBannerPreviewImage" src="" class="h-28 w-full object-cover rounded-lg border">
          </div>
          <div id="subBannerPlaceholder">
            <i class="fa-regular fa-image text-2xl text-slate-300 mb-1"></i>
            <p class="text-[11px] text-slate-500 max-w-md mx-auto">Recommended size is 1300×380 pixels. Max file size: 4MB.</p>
          </div>
          <input type="file" id="modal_sub_banner" name="banner" accept="image/*" class="hidden" onchange="openCropper(this, 1300/380, 'subBannerPreviewImage', 'subBannerPreviewContainer', 'subBannerPlaceholder')">
          <button type="button" onclick="document.getElementById('modal_sub_banner').click()" class="mt-2 px-4 py-1.5 bg-purple-50 text-[#541DFF] text-xs font-semibold rounded-lg">
            Add Image
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 items-start">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1.5">Image</label>
          <div class="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center bg-slate-50/50 min-h-[250px] flex flex-col items-center justify-center">
            <div id="subImagePreviewContainer" class="hidden mb-2">
              <img id="subImagePreviewImage" src="" class="w-24 h-24 object-cover rounded-xl border">
            </div>
            <div id="subImagePlaceholder">
              <i class="fa-regular fa-image text-2xl text-slate-300 mb-1"></i>
              <p class="text-[10.5px] text-slate-500">Recommended size is 500×500 pixels. Maximum file size is 4MB.</p>
            </div>
            <input type="file" id="modal_sub_image" name="image" accept="image/*" class="hidden" onchange="openCropper(this, 1, 'subImagePreviewImage', 'subImagePreviewContainer', 'subImagePlaceholder')">
            <button type="button" onclick="document.getElementById('modal_sub_image').click()" class="mt-2 px-4 py-1.5 bg-purple-50 text-[#541DFF] text-xs font-semibold rounded-lg">
              Add Image
            </button>
          </div>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1.5">Category Name *</label>
            <input type="text" name="name" id="modalSubCatName" maxlength="50" required placeholder="Category Name" oninput="document.getElementById('subNameCharCount').innerText = 50 - this.value.length" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs bg-slate-50/40">
            <div class="text-right text-[10px] text-slate-400 mt-1">Character limit: <span id="subNameCharCount">50</span></div>
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1.5">Short Description</label>
            <textarea name="short_description" id="modalSubCatDesc" rows="5" placeholder="Short description..." class="w-full border border-slate-200 rounded-xl p-3 text-xs bg-slate-50/40"></textarea>
          </div>
        </div>
      </div>

      <div class="flex gap-3 pt-4 border-t border-slate-100">
        <button type="button" onclick="closeSubCategoryModal()" class="flex-1 py-2.5 border border-slate-200 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-50">Cancel</button>
        <button type="submit" class="flex-1 py-2.5 bg-[#541DFF] hover:bg-[#4313d6] text-white rounded-xl text-xs font-bold shadow-md">Save</button>
      </div>
    </form>
  </div>
</div>

<script>
  function openSubCategoryModal() {
    document.getElementById('subModalTitle').innerText = 'Create sub-category';
    document.getElementById('sub_form_action').value = 'create_subcategory';
    document.getElementById('sub_pk_field').value = '';
    document.getElementById('modalSubCatName').value = '';
    document.getElementById('modalSubCatDesc').value = '';
    document.getElementById('createSubCategoryModal').classList.remove('hidden');
  }
  function openEditSubModal(pk, name, desc) {
    document.getElementById('subModalTitle').innerText = 'Edit sub-category';
    document.getElementById('sub_form_action').value = 'update_subcategory';
    document.getElementById('sub_pk_field').value = pk;
    document.getElementById('modalSubCatName').value = name;
    document.getElementById('modalSubCatDesc').value = desc;
    document.getElementById('createSubCategoryModal').classList.remove('hidden');
  }
  function closeSubCategoryModal() { document.getElementById('createSubCategoryModal').classList.add('hidden'); }
</script>
{% endblock %}
"""

# -------------------------------------------------------------
# 7. WRITE ALL FILES TO DISK SAFELY
# -------------------------------------------------------------
for filepath, content in FILES.items():
    folder = os.path.dirname(filepath)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Created / Updated: {filepath}")

# -------------------------------------------------------------
# 8. SELF-HEALING AUTOMATIC DATABASE MIGRATION
# -------------------------------------------------------------
print("\n" + "=" * 75)
print("⚙️  ডেটাবেজে মাইগ্রেশন ও ক্যাশ টেবিল অ্যাপ্লাই করা হচ্ছে...")
print("=" * 75)

try:
    subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
    subprocess.run([sys.executable, "manage.py", "createcachetable"])
    print("\n✅ সফল! ডেটাবেজ স্কিমা ১০০% আপ-টু-ডেট এবং মাইগ্রেশন সম্পন্ন।")
except Exception as e:
    print(f"Migration Notice: {e}")

print("=" * 75)
print("🎉 অভিনন্দন! সমস্ত ফাইল সাজানো এবং ডেটাবেজ ফিক্স সম্পন্ন।")
print("👉 এখন সার্ভার চালু করতে রান করুন: python main.py")
print("=" * 75)