from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, filters
from main.models import Order, Product, ProductCategory, Shipment, PaymentRequest, OrderMeta, Cart, User
from main.serializers import ProductSerializer, ProductCartSerializer
from rest_framework import generics, filters
from rest_framework.viewsets import ViewSet
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from main.cart import CartService

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

    def get(self, request):
        pass

    def post(self, request):

        response = {
            "status_code": 200,
            "status": "success",
            "data": {},
        }
        serializer = ProductCartSerializer(data=request.data, many=True)
        if not serializer.is_valid():    
            return serializer.errors
        
        CartService(user=User.objects.get(request.auth['user_id'])).add_products_to_cart(serialized_data=serializer.validated_data)

        return Response(data=response, status=HTTP_201_CREATED)


class OrderAPIViewSet(ViewSet):

    def get(self, request):
        pass

    def post(self, request):
        pass
