from django.core.validators import MinValueValidator
from django.db import models


class OutOfStockError(Exception):
    """Попытка купить больше товара, чем есть на складе."""


class Product(models.Model):
    """Товар магазина товаров для сада (вариант 11).

    У каждого товара есть начальное (initial_quantity) и текущее
    (quantity) количество на складе. После покупки количество
    уменьшается. Если оно уменьшилось более чем в два раза по сравнению
    с начальным, цена товара однократно возрастает на 20 %.
    """

    PRICE_INCREASE_PERCENT = 20

    name = models.CharField('название', max_length=200)
    price = models.PositiveIntegerField('цена, руб.')
    initial_quantity = models.PositiveIntegerField(
        'начальное количество', default=10)
    quantity = models.PositiveIntegerField('количество на складе', default=10)
    price_increased = models.BooleanField('цена повышена', default=False)

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ['id']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__lte=models.F('initial_quantity')),
                name='quantity_lte_initial_quantity',
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def is_available(self) -> bool:
        """Товар можно купить, только если он есть на складе."""
        return self.quantity > 0

    def is_stock_halved(self) -> bool:
        """Количество уменьшилось более чем в два раза:
        initial / quantity > 2  <=>  2 * quantity < initial."""
        return 2 * self.quantity < self.initial_quantity

    @classmethod
    def increased_price(cls, price: int) -> int:
        """Цена, увеличенная на 20 % с округлением до рубля."""
        return (price * (100 + cls.PRICE_INCREASE_PERCENT) + 50) // 100

    def sell(self, count: int = 1) -> None:
        """Списать проданный товар со склада и при необходимости поднять
        цену. Изменения сохраняются в базе данных."""
        if count < 1:
            raise ValueError('Количество должно быть положительным')
        if count > self.quantity:
            raise OutOfStockError(
                f'На складе только {self.quantity} шт. товара «{self.name}»')
        self.quantity -= count
        if not self.price_increased and self.is_stock_halved():
            self.price = self.increased_price(self.price)
            self.price_increased = True
        self.save(update_fields=['quantity', 'price', 'price_increased'])


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name='товар')
    person = models.CharField('покупатель', max_length=200)
    address = models.CharField('адрес доставки', max_length=200)
    count = models.PositiveIntegerField(
        'количество', default=1, validators=[MinValueValidator(1)])
    price = models.PositiveIntegerField('цена за единицу, руб.', default=0)
    date = models.DateTimeField('дата', auto_now_add=True)

    class Meta:
        verbose_name = 'покупка'
        verbose_name_plural = 'покупки'
        ordering = ['-date']

    def __str__(self):
        return f'{self.person}: {self.product} × {self.count}'

    @property
    def total(self) -> int:
        """Стоимость покупки."""
        return self.price * self.count
