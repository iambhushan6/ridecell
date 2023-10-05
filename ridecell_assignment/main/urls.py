from django.contrib import admin
from django.urls import path, include
from main.views import TestAPIView, CartAPIViewset, OrderAPIViewSet, PaymentWebhookAPIViewset, ShipmentWebhookAPIViewset

urlpatterns = [
    path('test/', TestAPIView, name='test_api_view'),
    path('cart/add-product/', CartAPIViewset.as_view({"get":"get", "post":"post"}), name='cart_api_view'),
    path('place-order/', OrderAPIViewSet.as_view({"get":"get", "post":"post"}), name='order_api_view'),
    path('payment-webhook/', PaymentWebhookAPIViewset.as_view({"post":"handle_webhook"}), name='payment_api_view'),
    path('shipment-webhook/', ShipmentWebhookAPIViewset.as_view({"post":"handle_webhook"}), name='shipment_api_view'),
]