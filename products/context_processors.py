from django.core.cache import cache
from django.db.models import Prefetch
from .models import SiteSetting, Category, Product


def site_settings_processor(request):
    site_setting = cache.get('global_site_settings')
    if not site_setting:
        site_setting = SiteSetting.get_settings()
        cache.set('global_site_settings', site_setting, timeout=300)

    global_categories = cache.get('global_active_categories')
    if global_categories is None:
        active_subs = Prefetch(
            'subcategories',
            queryset=Category.objects.filter(is_active=True).order_by('order', 'name'),
            to_attr='active_subcategories',
        )
        global_categories = list(
            Category.objects.filter(is_active=True, parent__isnull=True)
            .prefetch_related(active_subs)
            .order_by('order', 'name')
        )
        cache.set('global_active_categories', global_categories, timeout=300)

    cart_upsell_products = cache.get('cart_upsell_products')
    if cart_upsell_products is None:
        cart_upsell_products = list(
            Product.objects.filter(is_active=True, stock__gt=0)
            .order_by('price', '-created_at')[:3]
        )
        cache.set('cart_upsell_products', cart_upsell_products, timeout=300)

    return {
        'site_setting': site_setting,
        'global_categories': global_categories,
        'cart_upsell_products': cart_upsell_products,
    }
