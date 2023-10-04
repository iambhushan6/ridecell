from rest_framework import serializers
from main.models import Product
from rest_framework.exceptions import ValidationError


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'selling_price', 'quantity', 'category__name']


class ProductCartSerializer(serializers.Serializer):

    product = serializers.PrimaryKeyRelatedField(queryset= Product.objects.all())
    quantity = serializers.IntegerField()

    def validate(self, attrs):

        attrs = super().validate(attrs)
        product = attrs["product"]
        quantity = attrs["quantity"]

        if not product.available_quantity >= quantity:
            raise ValidationError({"error":"Item currently is not available in required quantity."})
        return attrs