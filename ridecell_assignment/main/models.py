from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ProductCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Product(models.Model):

    category = models.ForeignKey(ProductCategory, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=200, unique=True)
    selling_price = models.PositiveIntegerField()
    in_stock = models.BooleanField(default=False)
    available_quantity = models.IntegerField()


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    master_cart_uuid = models.UUIDField()


class Order(models.Model):

    class OrderStatuses(models.TextChoices):
        PLACED = 'placed'
        SHIPPED = 'shipped'
        DELIVERED = 'delivered'
        CANCELLED = 'cancelled'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_price = models.PositiveIntegerField()
    delivery_price = models.PositiveIntegerField(null=True)
    total_price = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=OrderStatuses.choices)
    third_party_identifier = models.CharField(max_length=200, null=True, blank=True)    # for 3p order identifier


class PaymentRequest(models.Model):

    class PaymentRequestStatus(models.TextChoices):
        CREATED = 'created'
        PROCESSED = 'processed'
        COMPLETED = 'completed'
        FAILED = 'failed'
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    total_payment = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=PaymentRequestStatus.choices)


class OrderMeta(models.Model):

    class OrderMetaKeys(models.TextChoices):
        PRODUCT_ID = 1
        PRODUCT_NAME = 2
        PRODUCT_QUANTITY = 3
        PRODUCT_SELLING_PRICE = 4
        PRODUCT_CATEGORY_NAME = 5
    
    key = models.IntegerField(choices=OrderMetaKeys.choices)
    value = models.JSONField(null=True)


class Shipment(models.Model):
    
    class ShipmentStatuses(models.TextChoices):
        SHIPPED = 'shipped'
        PICKED_UP = 'picked_up'
        IN_TRANSIT = 'in_transit'
        OUT_FOR_DELIVERY = 'out_for_delivery'
        DELIVERED = 'delivered'
        FAILED = 'failed'
        CANCELLED = 'cancelled'
        LOST = 'lost'
        DAMAGED = 'damaged'

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    third_party_identifier = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=ShipmentStatuses.choices)





