from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import CreateView

from .forms import PurchaseForm
from .models import Product, Purchase


def index(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'shop/index.html', context)


class PurchaseCreate(CreateView):
    """Оформление покупки товара (контроллер в терминах MVC)."""

    model = Purchase
    form_class = PurchaseForm

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=kwargs['product_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = self.product
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def post(self, request, *args, **kwargs):
        # Блокируем строку товара до конца транзакции, чтобы два
        # одновременных покупателя не купили один и тот же остаток.
        with transaction.atomic():
            self.product = Product.objects.select_for_update().get(
                pk=self.product.pk)
            if not self.product.is_available:
                self.object = None
                return self.render_to_response(self.get_context_data(
                    form=self.get_form()))
            return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        purchase = form.save(commit=False)
        purchase.product = self.product
        purchase.price = self.product.price
        purchase.save()
        old_price = self.product.price
        self.product.sell(purchase.count)
        self.object = purchase
        return render(self.request, 'shop/purchase_done.html', {
            'purchase': purchase,
            'product': self.product,
            'price_changed': self.product.price != old_price,
        })
