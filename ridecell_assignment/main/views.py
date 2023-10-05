from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, filters
from main.models import Order, Product, ProductCategory, Shipment, PaymentRequest, OrderMeta, Cart, User
from main.serializers import ProductSerializer, ProductCartSerializer
from rest_framework import generics, filters
from rest_framework.viewsets import ViewSet
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework import exceptions
from main.cart import CartService
from main.utils import success_response, error_response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import serializers
from main.order import OrderService


# Create your views here.

@api_view(["GET"])
def TestAPIView(request):

    if request.method == "GET":
        return Response({"data": "Ridecell Assignment"})
    
    return Response({"error": "Invalid request method."})


class ProductListView(generics.ListAPIView):
    '''
    Get api using ListAPIView with searching and filtering functionality.
    '''
    queryset = Product.objects.all().order_by("-published_at")
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter,]
    search_fields = ['name', 'category__name']    # Optimised search filter


class CartAPIViewset(ViewSet):

    def check_permissions(self, request):
        super().check_permissions(request)
        if not (
            isinstance(self.request.auth, AccessToken)
            and self.request.auth
        ):
            raise exceptions.PermissionDenied()

    def get(self, request):
        # Get api response of user's cart data.
        pass

    def post(self, request):

        serializer = ProductCartSerializer(data=request.data, many=True)
        if not serializer.is_valid():    
            return error_response(status=HTTP_400_BAD_REQUEST, errors=serializer.errors)
        
        status, master_cart_uuid = CartService(user=User.objects.get(request.auth['user_id'])).add_products_to_cart(serialized_data=serializer.validated_data)

        if not status:
            return error_response(status=HTTP_400_BAD_REQUEST, data={"errors": "Please try again!"})

        return success_response(status=HTTP_201_CREATED, data={"master_cart_uuid":master_cart_uuid})


class OrderAPIViewSet(ViewSet):

    def check_permissions(self, request):
        super().check_permissions(request)
        if not (
            isinstance(self.request.auth, AccessToken)
            and self.request.auth
        ):
            raise exceptions.PermissionDenied()

    def get(self, request):
        # Get api response of user's order data.
        pass

    def post(self, request):
        master_cart_uuid = request.data.get("master_cart_uuid")
        try:
            serializers.UUIDField().run_validation(data=master_cart_uuid)
        except serializers.ValidationError as e:
            return error_response(status=HTTP_400_BAD_REQUEST, msg="", data={"error": e.detail})
        
        cart_data = Cart.objects.filter(master_cart_uuid=master_cart_uuid, user=request.auth.user)
        if not cart_data:
            return error_response(status=HTTP_400_BAD_REQUEST, msg="", data={"error": "No carts present with provided cart uuid"})
        
        status, payment_link_or_err_msg = OrderService().validate_order(cart_data=cart_data)

        if not status:
            return error_response(status=HTTP_400_BAD_REQUEST, msg="", data={"error": payment_link_or_err_msg})
        return success_response(status=HTTP_200_OK, data={"payment_link": payment_link_or_err_msg})
    

class PaymentWebhookAPIViewset(ViewSet):

    def receive_webhook(self, request):

        order_id = request.data.get('order_id')

        if request.data.get("payment_status") == 'SUCCESSFUL':
            PaymentRequest.objects.filter(order_id=order_id).update(status=PaymentRequest.PaymentRequestStatus.COMPLETED)
            status, msg = OrderService(order_id=order_id).place_order()
            if status:
                # Here send socket event to user that payment is received and order has been placed.
                pass

        return success_response(status=HTTP_200_OK)