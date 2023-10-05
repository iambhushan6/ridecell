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
        CREATED = 'created'
        PLACED = 'placed'
        COMPLETED = 'completed'
        CANCELLED = 'cancelled'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_price = models.PositiveIntegerField()
    delivery_price = models.PositiveIntegerField(null=True)
    total_price = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=OrderStatuses.choices)
    third_party_identifier = models.CharField(max_length=200, null=True, blank=True)    # for 3p order identifier

class LineItem(models.Model):

    class LineItemStatus(models.TextChoices):
        CREATED = 'created'
        PROCESSED = 'processed'
        COMPLETED = 'completed'
        FAILED = 'failed'
        CANCELLED = 'cancelled'

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=LineItemStatus.choices)

class LineItemMeta(models.Model):

    class LineItemMetaKeys(models.TextChoices):
        PRODUCT_ID = 1
        PRODUCT_NAME = 2
        PRODUCT_QUANTITY = 3
        PRODUCT_SELLING_PRICE = 4
        PRODUCT_CATEGORY_NAME = 5
    
    line_item = models.ForeignKey(LineItem, on_delete= models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    key = models.IntegerField(choices=LineItemMetaKeys.choices)
    value = models.JSONField(null=True)


class PaymentRequest(models.Model):

    class PaymentRequestStatus(models.TextChoices):
        CREATED = 'created'
        PROCESSED = 'processed'
        COMPLETED = 'completed'
        FAILED = 'failed'
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    total_payment = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=PaymentRequestStatus.choices)


class Shipment(models.Model):
    
    class ShipmentStatuses(models.TextChoices):
        SHIPPED = 'shipped'
        PRINTED = 'printed'
        IN_TRANSIT = 'in_transit'
        OUT_FOR_DELIVERY = 'out_for_delivery'
        DELIVERED = 'delivered'
        FAILED = 'failed'
        CANCELLED = 'cancelled'
        LOST = 'lost'
        DAMAGED = 'damaged'

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    line_item = models.OneToOneField(LineItem, on_delete=models.CASCADE)
    third_party_identifier = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=20, choices=ShipmentStatuses.choices)





