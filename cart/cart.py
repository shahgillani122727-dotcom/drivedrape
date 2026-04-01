from products.models import Product


class Cart:
    """
    Session-based cart — works for both guests and logged-in users.
    No database needed. Fast and simple.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_qty=False):
        pid = str(product.id)
        if pid not in self.cart:
            self.cart[pid] = {
                'quantity': 0,
                'price': str(product.current_price),
                'name': product.name,
            }
        if override_qty:
            self.cart[pid]['quantity'] = quantity
        else:
            self.cart[pid]['quantity'] += quantity
        self.save()

    def remove(self, product):
        pid = str(product.id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session['cart'] = {}
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['total_price'] = float(item['price']) * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    @property
    def subtotal(self):
        return sum(float(item['price']) * item['quantity']
                   for item in self.cart.values())

    @property
    def total(self):
        return self.subtotal + 200  # Rs. 200 shipping flat rate


def cart_count(request):
    """Context processor — makes cart count available in ALL templates"""
    cart = Cart(request)
    return {'cart_count': len(cart)}
