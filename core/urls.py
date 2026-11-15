from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.contrib.sitemaps.views import sitemap
from products.sitemaps import ProductSitemap, CategorySitemap
from products.views import robots_txt_view, favicon_view, chrome_devtools_json_view

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
    path('favicon.ico', favicon_view, name='favicon'),
    path('.well-known/appspecific/com.chrome.devtools.json', chrome_devtools_json_view, name='chrome_devtools_json'),
    path('', include('products.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.BASE_DIR / 'static')

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
]
