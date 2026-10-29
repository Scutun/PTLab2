from django.core.management import call_command
from django.core.management.base import BaseCommand

from shop.models import Product


class Command(BaseCommand):
    help = ('Загружает товары из фикстуры products.yaml, только если '
            'таблица товаров пуста (не сбрасывает остатки при повторном '
            'развёртывании).')

    def handle(self, *args, **options):
        if Product.objects.exists():
            self.stdout.write('Товары уже есть в базе, загрузка пропущена.')
            return
        call_command('loaddata', 'products.yaml', verbosity=0)
        self.stdout.write(self.style.SUCCESS(
            f'Загружено товаров: {Product.objects.count()}'))
