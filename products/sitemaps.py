from django.contrib.sitemaps import Sitemap
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
