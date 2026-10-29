from django.test import Client, TestCase
from django.urls import reverse

from shop.models import Product, Purchase


class PurchaseCreateTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_webpage_accessibility(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class IndexViewTestCase(TestCase):
    def setUp(self):
        self.available = Product.objects.create(
            name="Секатор", price=900, initial_quantity=6, quantity=6)
        self.sold_out = Product.objects.create(
            name="Лейка", price=550, initial_quantity=3, quantity=0)

    def test_index_shows_products_and_stock(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, "Секатор")
        self.assertContains(response, "6 из 6")
        self.assertContains(response, reverse('buy', args=[self.available.id]))

    def test_index_marks_sold_out_product(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, "нет в наличии")
        self.assertNotContains(response,
                               reverse('buy', args=[self.sold_out.id]))


class BuyViewTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Лопата", price=1200, initial_quantity=10, quantity=10)
        self.url = reverse('buy', args=[self.product.id])
        self.data = {'person': 'Иванов', 'address': 'Садовая ул., 1',
                     'count': 1}

    def test_buy_page_contains_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/purchase_form.html')
        self.assertContains(response, 'name="count"')

    def test_buy_nonexistent_product_returns_404(self):
        response = self.client.get(reverse('buy', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_purchase_decreases_stock(self):
        self.data['count'] = 3
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Спасибо за покупку, Иванов!")
        self.assertContains(response, "3600 руб.")
        purchase = Purchase.objects.get()
        self.assertEqual(purchase.count, 3)
        self.assertEqual(purchase.price, 1200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 7)

    def test_purchase_increases_price_for_next_buyers(self):
        self.data['count'] = 6
        response = self.client.post(self.url, self.data)
        self.assertContains(response, "новая цена 1440 руб.")
        # покупатель оплатил по старой цене
        self.assertEqual(Purchase.objects.get().price, 1200)
        self.client.post(self.url, {**self.data, 'count': 1})
        self.assertEqual(Purchase.objects.latest('id').price, 1440)

    def test_cannot_buy_more_than_in_stock(self):
        self.data['count'] = 11
        response = self.client.post(self.url, self.data)
        self.assertContains(response, "На складе только 10 шт.")
        self.assertEqual(Purchase.objects.count(), 0)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 10)

    def test_cannot_buy_sold_out_product(self):
        Product.objects.filter(pk=self.product.pk).update(quantity=0)
        response = self.client.post(self.url, self.data)
        self.assertContains(response, "Товар закончился")
        self.assertEqual(Purchase.objects.count(), 0)

    def test_invalid_form_does_not_create_purchase(self):
        response = self.client.post(self.url, {'person': '', 'address': '',
                                               'count': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Purchase.objects.count(), 0)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 10)
