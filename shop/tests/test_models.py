from datetime import datetime

from django.test import TestCase

from shop.models import OutOfStockError, Product, Purchase


class ProductTestCase(TestCase):
    def setUp(self):
        Product.objects.create(name="book", price="740")
        Product.objects.create(name="pencil", price="50")

    def test_correctness_types(self):
        self.assertIsInstance(Product.objects.get(name="book").name, str)
        self.assertIsInstance(Product.objects.get(name="book").price, int)
        self.assertIsInstance(Product.objects.get(name="pencil").name, str)
        self.assertIsInstance(Product.objects.get(name="pencil").price, int)

    def test_correctness_data(self):
        self.assertTrue(Product.objects.get(name="book").price == 740)
        self.assertTrue(Product.objects.get(name="pencil").price == 50)


class PurchaseTestCase(TestCase):
    def setUp(self):
        self.product_book = Product.objects.create(name="book", price="740")
        self.datetime = datetime.now()
        Purchase.objects.create(product=self.product_book,
                                person="Ivanov",
                                address="Svetlaya St.")

    def test_correctness_types(self):
        purchase = Purchase.objects.get(product=self.product_book)
        self.assertIsInstance(purchase.person, str)
        self.assertIsInstance(purchase.address, str)
        self.assertIsInstance(purchase.date, datetime)

    def test_correctness_data(self):
        purchase = Purchase.objects.get(product=self.product_book)
        self.assertEqual(purchase.person, "Ivanov")
        self.assertEqual(purchase.address, "Svetlaya St.")
        self.assertEqual(purchase.date.replace(microsecond=0),
                         self.datetime.replace(microsecond=0))

    def test_total(self):
        purchase = Purchase(product=self.product_book, person="Petrov",
                            address="Lesnaya St.", count=3, price=740)
        self.assertEqual(purchase.total, 2220)


class ProductStockTestCase(TestCase):
    """Вариант 11: учёт остатков и повышение цены на 20 %."""

    def setUp(self):
        self.product = Product.objects.create(
            name="Лопата", price=1200, initial_quantity=10, quantity=10)

    def test_default_quantity(self):
        product = Product.objects.create(name="Грабли", price=650)
        self.assertEqual(product.initial_quantity, 10)
        self.assertEqual(product.quantity, 10)
        self.assertFalse(product.price_increased)

    def test_sell_decreases_quantity(self):
        self.product.sell(3)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 7)
        self.assertEqual(self.product.price, 1200)

    def test_sell_whole_stock_makes_product_unavailable(self):
        self.assertTrue(self.product.is_available)
        self.product.sell(10)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 0)
        self.assertFalse(self.product.is_available)

    def test_sell_more_than_stock_raises(self):
        with self.assertRaises(OutOfStockError):
            self.product.sell(11)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 10)

    def test_sell_non_positive_count_raises(self):
        with self.assertRaises(ValueError):
            self.product.sell(0)

    def test_price_not_increased_at_exactly_half(self):
        # 10 -> 5: уменьшилось ровно в два раза, а не более чем в два
        self.product.sell(5)
        self.product.refresh_from_db()
        self.assertFalse(self.product.price_increased)
        self.assertEqual(self.product.price, 1200)

    def test_price_increased_when_less_than_half(self):
        # 10 -> 4: уменьшилось в 2,5 раза
        self.product.sell(6)
        self.product.refresh_from_db()
        self.assertTrue(self.product.price_increased)
        self.assertEqual(self.product.price, 1440)

    def test_price_increased_only_once(self):
        self.product.sell(6)
        self.product.sell(2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 2)
        self.assertEqual(self.product.price, 1440)

    def test_price_increase_step_by_step(self):
        for _ in range(5):
            self.product.sell(1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 1200)
        self.product.sell(1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 1440)

    def test_odd_initial_quantity(self):
        product = Product.objects.create(
            name="Тачка", price=4800, initial_quantity=5, quantity=5)
        product.sell(2)                       # 5 -> 3: 3 * 2 = 6 > 5
        self.assertFalse(product.price_increased)
        product.sell(1)                       # 3 -> 2: 2 * 2 = 4 < 5
        self.assertTrue(product.price_increased)
        self.assertEqual(product.price, 5760)

    def test_increased_price_rounding(self):
        self.assertEqual(Product.increased_price(1000), 1200)
        self.assertEqual(Product.increased_price(999), 1199)   # 1198,8
        self.assertEqual(Product.increased_price(1), 1)        # 1,2
        self.assertEqual(Product.increased_price(3), 4)        # 3,6
