from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart(object):

    def __init__(self, request):
        """
        Ініціалізація корзини
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
  
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                    'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # Оновлення сесії cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Відмітити сеанс як змінений, щоб впевнитись, що він збережений
        self.session.modified = True

    def remove(self, product):

        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()