from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.views.generic import RedirectView
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
    # BUG FIX: browsers request /favicon.ico directly (ignoring the <link rel="icon">
    # tag in <head>), which previously had no matching URL pattern and returned a
    # noisy 404 in the console/logs on every page load. Redirect it to our SVG badge.
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'images/favicon.svg', permanent=True), name='favicon'),
    path('', include('products.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.BASE_DIR / 'static')

# BUG FIX: user-uploaded media (product/category images) was only served when DEBUG=True.
# This project has no S3/cloud storage backend configured, so without this, every product
# and category image returns 404 in production (gunicorn runs with DEBUG=False).
# WhiteNoise only serves STATIC_URL, never MEDIA_URL, so we must serve media ourselves here.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
]



