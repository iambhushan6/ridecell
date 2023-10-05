from main.models import Cart, Product, ProductCategory, User
from uuid import uuid4

class CartService:
    '''
    Handles cart related functionalities: 1. Adding products to cart and updating cart items
    '''

    def __init__(self, user: User) -> None:
        self.user = user

    def add_products_to_cart(self, serialized_data:dict):

        carts_to_be_created = []
        master_cart_uuid = uuid4()

        for data in serialized_data:
            carts_to_be_created.append(
                Cart(
                    user= self.user,
                    product= data['product'],
                    quantity= data['quantity'],
                    master_cart_uuid= master_cart_uuid
                )
            )
        Cart.objects.bulk_create(carts_to_be_created)

        return True, master_cart_uuid