#models.py

from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    #...
    quantity = models.PositiveIntegerField(default=0)  # New field for product quantity


    def __str__(self):
        return self.name

    @classmethod
    def search_by_name(cls, product_name):
        return cls.objects.filter(name__icontains=product_name)



class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def add_to_cart(self, product):
        cart_item, created = CartItem.objects.get_or_create(cart=self, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

    def remove_from_cart(self, product):
        try:
            cart_item = CartItem.objects.get(cart=self, product=product)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        except CartItem.DoesNotExist:
            pass

    def get_cart_total(self):
        cart_items = self.cartitem_set.all()
        return sum(item.get_total_price() for item in cart_items)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} - {self.cart}"

    def get_total_price(self):
        return self.product.price * self.quantity


class DeliveryInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"Delivery Info for {self.user.username}"