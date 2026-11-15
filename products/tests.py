import json
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Category, Product, SiteSetting

# The project's default cache backend is a DB-backed cache table that only
# exists after `manage.py createcachetable` has been run outside of tests.
# These tests exercise views that read/write cache (rate limiting, the
# order-cooldown guard, site-settings caching) so we swap in a plain
# in-memory cache for the duration of the test run.
TEST_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


@override_settings(CACHES=TEST_CACHES)
class RichOrderReceiptTests(TestCase):
    """Covers master-prompt section 1: place_order_api must return a full,
    itemized receipt payload -- not just status/order_id/total."""

    def setUp(self):
        SiteSetting.objects.get_or_create(pk=1)
        self.category = Category.objects.create(name="Key Rings")
        self.product_a = Product.objects.create(
            name="Key Ring", price=Decimal('200.00'), discount_price=Decimal('100.00'),
            stock=45, category=self.category,
        )
        self.product_b = Product.objects.create(
            name="Phone Cover", price=Decimal('300.00'),
            stock=10, category=self.category,
        )

    def _place_order(self, extra_items=None, promo_code=''):
        items = [
            {'id': self.product_a.id, 'qty': 2},
            {'id': self.product_b.id, 'qty': 1},
        ]
        if extra_items:
            items = extra_items
        payload = {
            'name': 'Mosabbir Ahmad',
            'phone': '01999999999',
            'district': 'Dhaka',
            'thana': 'Mirpur',
            'address': 'House 1, Road 2',
            'promo_code': promo_code,
            'items': items,
        }
        return self.client.post(
            reverse('place_order_api'),
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_backward_compatible_fields_still_present(self):
        res = self._place_order()
        data = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn('order_id', data)
        self.assertIn('total', data)

    def test_receipt_includes_customer_and_delivery_fields(self):
        res = self._place_order()
        data = res.json()
        self.assertEqual(data['customer_name'], 'Mosabbir Ahmad')
        self.assertEqual(data['customer_phone'], '01999999999')
        self.assertEqual(data['district'], 'Dhaka')
        self.assertEqual(data['thana'], 'Mirpur')
        self.assertEqual(data['shipping_address'], 'House 1, Road 2')
        self.assertEqual(data['delivery_zone'], 'Inside Dhaka')
        self.assertEqual(data['estimated_delivery'], "1–2 Business Days")

    def test_receipt_estimated_delivery_outside_dhaka(self):
        res = self.client.post(
            reverse('place_order_api'),
            data=json.dumps({
                'name': 'Mosabbir Ahmad', 'phone': '01999999999', 'district': 'Sylhet',
                'address': 'Somewhere', 'items': [{'id': self.product_a.id, 'qty': 1}],
            }),
            content_type='application/json',
        )
        data = res.json()
        self.assertEqual(data['delivery_zone'], 'Outside Dhaka')
        self.assertEqual(data['estimated_delivery'], "2–4 Business Days")

    def test_receipt_price_breakdown_math(self):
        res = self._place_order()
        data = res.json()
        setting = SiteSetting.get_settings()
        # 2 x effective_price(100.00) + 1 x effective_price(300.00) = 500.00
        self.assertEqual(Decimal(data['subtotal']), Decimal('500.00'))
        self.assertEqual(Decimal(data['delivery_fee']), setting.delivery_fee_dhaka)
        expected_total = Decimal('500.00') + setting.delivery_fee_dhaka
        self.assertEqual(Decimal(data['total']), expected_total)

    def test_receipt_items_array_has_full_line_item_detail(self):
        res = self._place_order()
        data = res.json()
        self.assertEqual(len(data['items']), 2)
        by_name = {i['name']: i for i in data['items']}

        key_ring_line = by_name['Key Ring']
        self.assertEqual(key_ring_line['qty'], 2)
        self.assertEqual(Decimal(key_ring_line['price']), Decimal('100.00'))  # effective, not regular
        self.assertEqual(Decimal(key_ring_line['line_total']), Decimal('200.00'))
        self.assertIn('code', key_ring_line)
        self.assertIn('image', key_ring_line)

        cover_line = by_name['Phone Cover']
        self.assertEqual(cover_line['qty'], 1)
        self.assertEqual(Decimal(cover_line['line_total']), Decimal('300.00'))

    def test_invalid_items_returns_clear_error_without_crashing(self):
        res = self.client.post(
            reverse('place_order_api'),
            data=json.dumps({
                'name': 'A', 'phone': '019', 'district': 'Dhaka', 'address': 'X',
                'items': [{'id': 999999, 'qty': 1}],
            }),
            content_type='application/json',
        )
        data = res.json()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data.get('status'), 'error')
        self.assertTrue(data.get('invalid_items'))


@override_settings(CACHES=TEST_CACHES)
class CategoryPageSortFilterCountTests(TestCase):
    """Covers master-prompt section 4: accurate subcategory item counts
    ("0 items" bug) plus the new sort/filter toolbar in shop_category_view."""

    def setUp(self):
        SiteSetting.objects.get_or_create(pk=1)
        self.parent = Category.objects.create(name="Key Ring VV")
        self.sub = Category.objects.create(name="kskashi", parent=self.parent)
        self.other_sub = Category.objects.create(name="Empty Sub", parent=self.parent)

        self.cheap = Product.objects.create(name="Cheap Item", price=Decimal('50.00'), stock=5, category=self.sub)
        self.pricey = Product.objects.create(name="Pricey Item", price=Decimal('500.00'), stock=0, category=self.sub)
        self.discounted = Product.objects.create(
            name="Discounted Item", price=Decimal('400.00'), discount_price=Decimal('100.00'),
            stock=3, category=self.parent,
        )
        # Inactive product must never count.
        Product.objects.create(name="Hidden", price=Decimal('10.00'), stock=5, category=self.sub, is_active=False)

    def test_homepage_category_card_counts_direct_plus_subcategory_products(self):
        # BUG FIX regression test: parent.products.count() alone used to be 0
        # even though 3 active products exist once subcategories are included.
        self.assertEqual(self.parent.total_active_products, 3)
        self.assertEqual(self.other_sub.total_active_products, 0)

    def test_category_view_shows_all_active_products_across_subcategories(self):
        res = self.client.get(reverse('shop_category', args=[self.parent.slug]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['products'].paginator.count, 3)

    def test_subcategory_filter_chip_counts(self):
        res = self.client.get(reverse('shop_category', args=[self.parent.slug]))
        counts = {c.name: c.active_product_count for c in res.context['subcategories']}
        self.assertEqual(counts['kskashi'], 2)
        self.assertEqual(counts['Empty Sub'], 0)

    def test_sub_filter_param_scopes_to_that_subcategory_only(self):
        res = self.client.get(reverse('shop_category', args=[self.parent.slug]), {'sub': self.sub.id})
        self.assertEqual(res.context['products'].paginator.count, 2)
        self.assertEqual(res.context['selected_sub'], self.sub)

    def test_in_stock_filter_excludes_zero_stock_items(self):
        res = self.client.get(reverse('shop_category', args=[self.parent.slug]), {'in_stock': '1'})
        names = {p.name for p in res.context['products']}
        self.assertNotIn('Pricey Item', names)  # stock=0
        self.assertIn('Cheap Item', names)

    def test_sort_price_asc_orders_by_effective_price(self):
        res = self.client.get(reverse('shop_category', args=[self.parent.slug]), {'sort': 'price_asc'})
        names = [p.name for p in res.context['products']]
        self.assertEqual(names, ['Cheap Item', 'Discounted Item', 'Pricey Item'])

    def test_sort_price_desc_orders_by_effective_price_descending(self):
        res = self.client.get(reverse('shop_category', args=[self.parent.slug]), {'sort': 'price_desc'})
        names = [p.name for p in res.context['products']]
        self.assertEqual(names, ['Pricey Item', 'Discounted Item', 'Cheap Item'])

    def test_sort_discount_prioritizes_biggest_discount_amount(self):
        res = self.client.get(reverse('shop_category', args=[self.parent.slug]), {'sort': 'discount'})
        names = [p.name for p in res.context['products']]
        self.assertEqual(names[0], 'Discounted Item')

    def test_pagination_querystring_preserves_sort_and_filter(self):
        res = self.client.get(
            reverse('shop_category', args=[self.parent.slug]),
            {'sort': 'price_asc', 'in_stock': '1'},
        )
        qs = res.context['pagination_qs']
        self.assertIn('sort=price_asc', qs)
        self.assertIn('in_stock=1', qs)
        self.assertNotIn('page=', qs)


@override_settings(CACHES=TEST_CACHES)
class FaviconTests(TestCase):
    """Covers master-prompt section 6: /favicon.ico must never 404."""

    def test_favicon_returns_200_not_404(self):
        res = self.client.get('/favicon.ico')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'image/svg+xml')


@override_settings(CACHES=TEST_CACHES)
class PageRenderSmokeTests(TestCase):
    """Basic 200-OK smoke tests for the redesigned storefront pages."""

    def setUp(self):
        SiteSetting.objects.get_or_create(pk=1)
        self.category = Category.objects.create(name="Accessories")
        self.product = Product.objects.create(
            name="Sample Product", price=Decimal('150.00'), stock=10, category=self.category,
        )

    def test_home_page_renders(self):
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)

    def test_category_page_renders(self):
        res = self.client.get(reverse('shop_category', args=[self.category.slug]))
        self.assertEqual(res.status_code, 200)

    def test_product_detail_page_renders(self):
        res = self.client.get(reverse('product_detail', args=[self.product.pk]))
        self.assertEqual(res.status_code, 200)

    def test_robots_txt_renders(self):
        res = self.client.get(reverse('robots_txt'))
        self.assertEqual(res.status_code, 200)



