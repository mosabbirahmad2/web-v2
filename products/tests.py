import io
import json
import os
import tempfile
from decimal import Decimal
from PIL import Image

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Category, Order, Product, ProductImage, ProductReview, ShowcaseSection, SiteSetting

TEST_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
TEST_STATIC_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


def make_test_image_file(name="test.png", color=(255, 0, 0, 255), mode="RGBA", size=(120, 120)):
    buf = io.BytesIO()
    img = Image.new(mode, size, color)
    img.save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")


@override_settings(CACHES=TEST_CACHES, STATICFILES_STORAGE=TEST_STATIC_STORAGE)
class RichOrderReceiptTests(TestCase):
    def setUp(self):
        cache.clear()
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
        self.assertEqual(data['estimated_delivery'], "1\u20132 Business Days")

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
        self.assertEqual(data['estimated_delivery'], "2\u20134 Business Days")

    def test_receipt_price_breakdown_math(self):
        res = self._place_order()
        data = res.json()
        setting = SiteSetting.get_settings()
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
        self.assertEqual(Decimal(key_ring_line['price']), Decimal('100.00'))
        self.assertEqual(Decimal(key_ring_line['line_total']), Decimal('200.00'))
        cover_line = by_name['Phone Cover']
        self.assertEqual(cover_line['qty'], 1)
        self.assertEqual(Decimal(cover_line['line_total']), Decimal('300.00'))

    def test_invalid_items_returns_clear_error_without_crashing(self):
        res = self.client.post(
            reverse('place_order_api'),
            data=json.dumps({
                'name': 'A', 'phone': '01999999999', 'district': 'Dhaka', 'address': 'X',
                'items': [{'id': 999999, 'qty': 1}],
            }),
            content_type='application/json',
        )
        data = res.json()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data.get('status'), 'error')
        self.assertTrue(data.get('invalid_items'))


@override_settings(CACHES=TEST_CACHES, STATICFILES_STORAGE=TEST_STATIC_STORAGE)
class CategoryPageSortFilterCountTests(TestCase):
    def setUp(self):
        cache.clear()
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
        Product.objects.create(name="Hidden", price=Decimal('10.00'), stock=5, category=self.sub, is_active=False)

    def test_homepage_category_card_counts_direct_plus_subcategory_products(self):
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
        self.assertNotIn('Pricey Item', names)
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


@override_settings(CACHES=TEST_CACHES, STATICFILES_STORAGE=TEST_STATIC_STORAGE)
class FaviconAndDevToolsTests(TestCase):
    def test_favicon_returns_200_not_404(self):
        res = self.client.get('/favicon.ico')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'image/svg+xml')

    def test_chrome_devtools_well_known_returns_200(self):
        res = self.client.get('/.well-known/appspecific/com.chrome.devtools.json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {})


@override_settings(CACHES=TEST_CACHES, STATICFILES_STORAGE=TEST_STATIC_STORAGE)
class AdminInPlaceImageUpdateTests(TestCase):
    def setUp(self):
        cache.clear()
        self._tmp = tempfile.TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self._tmp.name)
        self.override.enable()

        SiteSetting.objects.get_or_create(pk=1)
        self.staff_user = User.objects.create_user(username='admin', password='pw', is_staff=True)
        self.normal_user = User.objects.create_user(username='buyer', password='pw', is_staff=False)

        self.cat = Category.objects.create(name="Key Rings", image=make_test_image_file("cat.png"))
        self.prod = Product.objects.create(
            name="Ring 1", price=Decimal('100.00'), stock=10,
            category=self.cat, image=make_test_image_file("prod.png")
        )
        self.gallery_img = ProductImage.objects.create(
            product=self.prod, image=make_test_image_file("gal.png")
        )

    def tearDown(self):
        self.override.disable()
        self._tmp.cleanup()

    def test_requires_authentication(self):
        res = self.client.post(reverse('merchant_update_image'), {
            'model_type': 'product_main',
            'object_id': self.prod.pk,
            'image': make_test_image_file("new.png"),
        })
        self.assertEqual(res.status_code, 302)

    def test_requires_staff_permission(self):
        self.client.login(username='buyer', password='pw')
        res = self.client.post(reverse('merchant_update_image'), {
            'model_type': 'product_main',
            'object_id': self.prod.pk,
            'image': make_test_image_file("new.png"),
        })
        self.assertEqual(res.status_code, 403)

    def test_product_main_image_replacement_cleans_old_file(self):
        self.client.login(username='admin', password='pw')
        old_path = self.prod.image.path
        self.assertTrue(os.path.exists(old_path))

        res = self.client.post(reverse('merchant_update_image'), {
            'model_type': 'product_main',
            'object_id': self.prod.pk,
            'image': make_test_image_file("updated_main.png", color=(0, 255, 0, 255)),
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('.webp?v=', data['new_url'])

        self.prod.refresh_from_db()
        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(os.path.exists(self.prod.image.path))

    def test_product_gallery_image_replacement_cleans_old_file(self):
        self.client.login(username='admin', password='pw')
        old_path = self.gallery_img.image.path
        self.assertTrue(os.path.exists(old_path))

        res = self.client.post(reverse('merchant_update_image'), {
            'model_type': 'product_gallery',
            'object_id': self.gallery_img.pk,
            'image': make_test_image_file("updated_gal.png", color=(0, 0, 255, 255)),
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['status'], 'success')

        self.gallery_img.refresh_from_db()
        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(os.path.exists(self.gallery_img.image.path))

    def test_category_and_site_logo_replacement_and_alpha_preserved(self):
        self.client.login(username='admin', password='pw')
        res = self.client.post(reverse('merchant_update_image'), {
            'model_type': 'category_image',
            'object_id': self.cat.pk,
            'image': make_test_image_file("cat_new.png"),
        })
        self.assertEqual(res.status_code, 200)

        res_logo = self.client.post(reverse('merchant_update_image'), {
            'model_type': 'site_logo',
            'object_id': 1,
            'image': make_test_image_file("logo.png", color=(0, 0, 0, 0)),
        })
        self.assertEqual(res_logo.status_code, 200)
        setting = SiteSetting.get_settings()
        self.assertTrue(bool(setting.logo))
        with Image.open(setting.logo.path) as im:
            self.assertIn('A', im.mode)

        home_res = self.client.get(reverse('home'))
        self.assertContains(home_res, setting.logo.url)

    def test_invalid_model_type_returns_400(self):
        self.client.login(username='admin', password='pw')
        res = self.client.post(reverse('merchant_update_image'), {
            'model_type': 'invalid_type',
            'object_id': 1,
            'image': make_test_image_file("x.png"),
        })
        self.assertEqual(res.status_code, 400)


@override_settings(CACHES=TEST_CACHES, STATICFILES_STORAGE=TEST_STATIC_STORAGE)
class PageRenderSmokeTests(TestCase):
    def setUp(self):
        cache.clear()
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


@override_settings(CACHES=TEST_CACHES, STATICFILES_STORAGE=TEST_STATIC_STORAGE)
class StorefrontAuditFixesTests(TestCase):
    def setUp(self):
        cache.clear()
        self.setting = SiteSetting.get_settings()
        self.active_cat = Category.objects.create(name="Cases", is_active=True)
        self.inactive_cat = Category.objects.create(name="Hidden Cat", is_active=False)
        self.active_prod = Product.objects.create(
            name="Leather Case", price=Decimal('350.00'), stock=10, category=self.active_cat, is_active=True
        )
        self.inactive_prod = Product.objects.create(
            name="Disabled Case", price=Decimal('250.00'), stock=10, category=self.active_cat, is_active=False
        )

    def test_inactive_category_returns_404(self):
        res = self.client.get(reverse('shop_category', args=[self.inactive_cat.slug]))
        self.assertEqual(res.status_code, 404)

    def test_inactive_product_returns_404(self):
        res = self.client.get(reverse('product_detail', args=[self.inactive_prod.pk]))
        self.assertEqual(res.status_code, 404)

    def test_showcase_hides_inactive_products_on_homepage(self):
        sec = ShowcaseSection.objects.create(title="Flash Picks", is_active=True)
        sec.products.add(self.active_prod, self.inactive_prod)
        res = self.client.get(reverse('home'))
        self.assertContains(res, "Leather Case")
        self.assertNotContains(res, "Disabled Case")

    def test_review_and_order_do_not_double_escape_quotes_or_ampersands(self):
        self.client.post(reverse('add_product_review', args=[self.active_prod.pk]), {
            'name': "O'Brien & Co",
            'rating': 'invalid_rating',
            'comment': "It's sleek & sturdy!",
        })
        review = ProductReview.objects.get(product=self.active_prod)
        self.assertEqual(review.customer_name, "O'Brien & Co")
        self.assertEqual(review.comment, "It's sleek & sturdy!")
        self.assertEqual(review.rating, 5)

        res = self.client.post(
            reverse('place_order_api'),
            data=json.dumps({
                'name': "O'Brien & Son",
                'phone': '01999999999',
                'district': 'Dhaka',
                'address': "House #5, 'Green' Road & Lane",
                'items': [{'id': self.active_prod.id, 'qty': 1}],
            }),
            content_type='application/json',
        )
        self.assertEqual(res.status_code, 200)
        order = Order.objects.latest('id')
        self.assertEqual(order.customer_name, "O'Brien & Son")
        self.assertEqual(order.shipping_address, "House #5, 'Green' Road & Lane")

    def test_whatsapp_link_number_normalizes_bd_local_number(self):
        self.setting.whatsapp_number = "01999999999"
        self.assertEqual(self.setting.whatsapp_link_number, "8801999999999")
        self.setting.whatsapp_number = "+880 1711-000000"
        self.assertEqual(self.setting.whatsapp_link_number, "8801711000000")

    def test_category_page_has_single_meta_description_tag(self):
        res = self.client.get(reverse('shop_category', args=[self.active_cat.slug]))
        html = res.content.decode('utf-8')
        self.assertEqual(html.count('<meta name="description"'), 1)

    def test_product_detail_respects_enable_buy_now_setting(self):
        self.setting.enable_buy_now = False
        self.setting.save()
        res = self.client.get(reverse('product_detail', args=[self.active_prod.pk]))
        self.assertNotContains(res, 'onclick="buyNowFromDetail()"')

        self.setting.enable_buy_now = True
        self.setting.save()
        res2 = self.client.get(reverse('product_detail', args=[self.active_prod.pk]))
        self.assertContains(res2, 'onclick="buyNowFromDetail()"')

    def test_invalid_phone_returns_400_on_checkout(self):
        res = self.client.post(
            reverse('place_order_api'),
            data=json.dumps({
                'name': 'Tester',
                'phone': '123',
                'district': 'Dhaka',
                'address': 'Road 1',
                'items': [{'id': self.active_prod.id, 'qty': 1}],
            }),
            content_type='application/json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['status'], 'error')

    def test_homepage_carousel_caps_at_8_products_while_preserving_total_count(self):
        for i in range(10):
            Product.objects.create(
                name=f"Extra Ring {i}", price=Decimal('100.00'), stock=5, category=self.active_cat
            )
        res = self.client.get(reverse('home'))
        cat_in_ctx = next(c for c in res.context['categories'] if c.pk == self.active_cat.pk)
        self.assertEqual(len(cat_in_ctx.carousel_products), 8)
        self.assertEqual(cat_in_ctx.home_product_count, 11)
@override_settings(CACHES=TEST_CACHES, STATICFILES_STORAGE=TEST_STATIC_STORAGE)
class UxPsychologyUpgradeTests(TestCase):
    def setUp(self):
        cache.clear()
        self.setting = SiteSetting.get_settings()
        self.setting.free_delivery_threshold = Decimal('600.00')
        self.setting.save()
        self.cat = Category.objects.create(name="Covers", is_active=True)
        self.cheap = Product.objects.create(
            name="Budget Key Ring", price=Decimal('150.00'), stock=10, category=self.cat, is_active=True
        )
        self.expensive = Product.objects.create(
            name="MagSafe Pro Case", price=Decimal('800.00'), discount_price=Decimal('650.00'),
            stock=10, category=self.cat, is_active=True
        )

    def test_free_delivery_threshold_sets_delivery_fee_to_zero_when_met(self):
        res = self.client.post(
            reverse('place_order_api'),
            data=json.dumps({
                'name': 'Mosabbir',
                'phone': '01999999999',
                'district': 'Chittagong',
                'address': 'Road 5',
                'items': [{'id': self.expensive.id, 'qty': 1}],
            }),
            content_type='application/json',
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(Decimal(data['delivery_fee']), Decimal('0.00'))
        self.assertEqual(Decimal(data['total']), Decimal('650.00'))

    def test_order_track_view_matches_order_id_and_phone_digits(self):
        order = Order.objects.create(
            customer_name="Rahim", customer_phone="01911223344",
            district="Dhaka", shipping_address="Mirpur", total_amount=Decimal('220.00'),
        )
        res_ok = self.client.get(reverse('order_track'), {'order_id': order.order_id, 'phone': '+8801911223344'})
        self.assertContains(res_ok, order.order_id)
        self.assertEqual(res_ok.context['tracked_order'], order)

        res_bad = self.client.get(reverse('order_track'), {'order_id': order.order_id, 'phone': '01700000000'})
        self.assertIsNone(res_bad.context['tracked_order'])
        self.assertContains(res_bad, 'No matching order found')

    def test_home_quick_filters_under300_and_sale(self):
        res_u = self.client.get(reverse('home'), {'filter': 'under300'})
        names_u = [p.name for p in res_u.context['products']]
        self.assertIn('Budget Key Ring', names_u)
        self.assertNotIn('MagSafe Pro Case', names_u)

        res_s = self.client.get(reverse('home'), {'filter': 'sale'})
        names_s = [p.name for p in res_s.context['products']]
        self.assertIn('MagSafe Pro Case', names_s)
        self.assertNotIn('Budget Key Ring', names_s)

    def test_product_card_hides_sku_and_shows_second_image_hover(self):
        ProductImage.objects.create(product=self.cheap, image=make_test_image_file("alt.png"))
        self.cheap.image = make_test_image_file("main.png")
        self.cheap.save()
        res = self.client.get(reverse('home'))
        self.assertNotContains(res, f"SKU: {self.cheap.product_code}")
        self.assertContains(res, 'card-img-secondary')
@override_settings(CACHES=TEST_CACHES, STATICFILES_STORAGE=TEST_STATIC_STORAGE)
class RedesignAndCustomizerTests(TestCase):
    def setUp(self):
        cache.clear()
        self._tmp = tempfile.TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self._tmp.name)
        self.override.enable()

        self.setting = SiteSetting.get_settings()
        self.staff = User.objects.create_user(username='admin2', password='pw', is_staff=True)
        self.cat = Category.objects.create(
            name="Key Rings", is_active=True,
            image=make_test_image_file("cat_i.png"),
            banner=make_test_image_file("cat_b.png"),
        )
        self.prod = Product.objects.create(
            name="Anime Key Ring", price=Decimal('700.00'), stock=10,
            category=self.cat, image=make_test_image_file("p_main.png"), is_active=True
        )

    def tearDown(self):
        self.override.disable()
        self._tmp.cleanup()

    def test_hero_banner_enforces_exact_1200x500_dimensions(self):
        from .models import HeroBanner
        hb = HeroBanner.objects.create(
            title="Eid Banner", image=make_test_image_file("wide.png", size=(800, 800)), link="/#all-products-section"
        )
        with Image.open(hb.image.path) as im:
            self.assertEqual(im.size, (1200, 500))

    def test_homepage_shows_dazzle_hero_carousel_and_hides_old_hero_and_trust_pillars(self):
        from .models import HeroBanner
        HeroBanner.objects.create(title="Slide 1", image=make_test_image_file("s1.png", size=(1200, 500)))
        res = self.client.get(reverse('home'))
        self.assertContains(res, 'dazzleHeroTrack')
        self.assertNotContains(res, 'NEW DROP 2026')
        self.assertNotContains(res, 'Check Before You Pay')

    def test_showcase_section_is_full_width_and_uses_see_all_button(self):
        sec = ShowcaseSection.objects.create(title="Trending Picks", background_style='brown', is_active=True)
        sec.products.add(self.prod)
        res = self.client.get(reverse('home'))
        self.assertContains(res, 'See all')
        self.assertContains(res, 'bg-[#5C3214] text-white')

    def test_brand_name_and_font_render_beside_logo_and_favicon_updates(self):
        self.client.login(username='admin2', password='pw')
        res = self.client.post(reverse('merchant_customize_theme'), {
            'site_name': 'Phoenix Hub',
            'brand_font': 'Playfair Display',
            'show_brand_name_with_logo': 'yes',
            'theme_color': '#5C3214',
            'theme_mode': 'light',
            'enable_buy_now': 'yes',
            'enable_free_delivery': 'yes',
            'free_delivery_threshold': '500',
            'delivery_fee_dhaka': '70',
            'delivery_fee_outside': '130',
            'contact_phone': '01999999999',
            'whatsapp_number': '01999999999',
            'contact_email': 'test@example.com',
            'office_address': 'Dhaka',
            'meta_title': 'Fantacy Tech - Premium Mobile Covers & Accessories',
            'logo': make_test_image_file("bird.png"),
        })
        self.assertEqual(res.status_code, 302)
        self.setting.refresh_from_db()
        self.assertEqual(self.setting.brand_font, 'Playfair Display')
        self.assertTrue(self.setting.meta_title.startswith('Phoenix Hub'))

        home_res = self.client.get(reverse('home'))
        self.assertContains(home_res, 'Phoenix Hub')
        self.assertContains(home_res, self.setting.logo.url)
        self.assertContains(home_res, 'Playfair+Display')

        fav_res = self.client.get('/favicon.ico')
        self.assertEqual(fav_res.status_code, 200)
        self.assertIn('image/', fav_res['Content-Type'])

    def test_enable_free_delivery_toggle_controls_checkout_fee(self):
        self.setting.enable_free_delivery = False
        self.setting.free_delivery_threshold = Decimal('600.00')
        self.setting.save()
        res = self.client.post(
            reverse('place_order_api'),
            data=json.dumps({
                'name': 'Buyer', 'phone': '01999999999', 'district': 'Dhaka',
                'address': 'Road 1', 'items': [{'id': self.prod.id, 'qty': 1}],
            }),
            content_type='application/json',
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Decimal(res.json()['delivery_fee']), self.setting.delivery_fee_dhaka)

    def test_remove_product_main_image_and_category_images(self):
        self.client.login(username='admin2', password='pw')
        self.client.post(reverse('merchant_edit_product', args=[self.prod.pk]), {
            'name': self.prod.name, 'price': '700.00', 'stock': '10', 'remove_main_image': '1',
        })
        self.prod.refresh_from_db()
        self.assertFalse(bool(self.prod.image))

        self.client.post(reverse('merchant_category_detail', args=[self.cat.pk]), {
            'action': 'update_category', 'name': self.cat.name,
            'remove_banner': '1', 'remove_image': '1',
        })
        self.cat.refresh_from_db()
        self.assertFalse(bool(self.cat.banner))
        self.assertFalse(bool(self.cat.image))

    def test_hero_banner_crud_add_edit_toggle_delete(self):
        from .models import HeroBanner
        self.client.login(username='admin2', password='pw')
        self.client.post(reverse('merchant_add_hero_banner'), {
            'title': 'B1', 'link': '/#all-products-section', 'order': '1',
            'image': make_test_image_file("b1.png", size=(1200, 500)),
        })
        hb = HeroBanner.objects.get(title='B1')
        self.client.post(reverse('merchant_toggle_hero_banner', args=[hb.pk]))
        hb.refresh_from_db()
        self.assertFalse(hb.is_active)
        self.client.post(reverse('merchant_delete_hero_banner', args=[hb.pk]))
        self.assertFalse(HeroBanner.objects.filter(pk=hb.pk).exists())
