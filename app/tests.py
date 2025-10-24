from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from app.models import Product


class CreateProductViewTests(TestCase):
    def setUp(self):
        # create a staff user
        self.staff_user = User.objects.create_user(username="admin", password="pass")
        self.staff_user.is_staff = True
        self.staff_user.save()

        # create a normal user
        self.normal_user = User.objects.create_user(username="user", password="pass")
        self.normal_user.is_staff = False
        self.normal_user.save()

        self.create_url = reverse("create_product")
        self.price_list_url = reverse("price_list")

    def test_get_anonymous_redirects_to_login(self):
        response = self.client.get(self.create_url)
        # @login_required should redirect anonymous users to the login page (302)
        self.assertEqual(response.status_code, 302)

    def test_get_staff_shows_form(self):
        self.client.login(username="admin", password="pass")
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        # template should include the form fields
        self.assertContains(response, 'name="name"', msg_prefix="Form should contain name field")
        self.assertContains(response, 'name="current_price"', msg_prefix="Form should contain current_price field")

    def test_get_authenticated_non_staff_redirects(self):
        # Authenticated but not staff — user_passes_test will reject
        self.client.login(username="user", password="pass")
        response = self.client.get(self.create_url)
        # The decorator will redirect (302)
        self.assertEqual(response.status_code, 302)

    def test_post_valid_creates_product_and_redirects(self):
        self.client.login(username="admin", password="pass")
        payload = {"name": "New Product", "current_price": "19.99"}
        before_count = Product.objects.count()
        response = self.client.post(self.create_url, data=payload)
        # On success the view redirects to the price list
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Product.objects.count(), before_count + 1)
        product = Product.objects.get(name="New Product")
        self.assertEqual(product.current_price, Decimal("19.99"))

    def test_post_missing_name_shows_error_and_does_not_create(self):
        self.client.login(username="admin", password="pass")
        payload = {"name": "", "current_price": "9.99"}
        before_count = Product.objects.count()
        response = self.client.post(self.create_url, data=payload, follow=True)
        self.assertEqual(Product.objects.count(), before_count)
        # follow=True -> final response should be 200 and contain message text
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product name is required")

    def test_post_invalid_price_shows_error_and_does_not_create(self):
        self.client.login(username="admin", password="pass")
        payload = {"name": "BadPrice", "current_price": "abc"}
        before_count = Product.objects.count()
        response = self.client.post(self.create_url, data=payload, follow=True)
        self.assertEqual(Product.objects.count(), before_count)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter valid price (e.g. 199.99).")

    def test_post_negative_price_shows_error_and_does_not_create(self):
        self.client.login(username="admin", password="pass")
        payload = {"name": "Negative", "current_price": "-5.00"}
        before_count = Product.objects.count()
        response = self.client.post(self.create_url, data=payload, follow=True)
        self.assertEqual(Product.objects.count(), before_count)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Price cannot be negative.")