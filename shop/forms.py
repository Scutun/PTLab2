from django import forms

from .models import Purchase


class PurchaseForm(forms.ModelForm):
    """Форма покупки. Проверяет, что товара на складе достаточно."""

    class Meta:
        model = Purchase
        fields = ['person', 'address', 'count']
        labels = {
            'person': 'Ваше имя',
            'address': 'Адрес доставки',
            'count': 'Количество, шт.',
        }

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
        self.fields['count'].min_value = 1
        self.fields['count'].widget.attrs['min'] = 1
        if product is not None:
            self.fields['count'].widget.attrs['max'] = product.quantity

    def clean_count(self):
        count = self.cleaned_data['count']
        if self.product is not None and count > self.product.quantity:
            raise forms.ValidationError(
                f'На складе только {self.product.quantity} шт.')
        return count
