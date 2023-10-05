from main.models import Cart, Product, ProductCategory, PaymentRequest, Shipment, Order, LineItem, LineItemMeta
from typing import List
from main.payment import PaymentService
from django.db import transaction
from main.shipment import ShipmentService
class OrderService:

    def __init__(self, order_id:int = None) -> None:
        self.order_id = order_id

    def create_line_item_metas():
        # creating line_item_meta instances here according to required product, category and lineitem data.
        pass

    def sync_product_quantity():
        # sync product available_quantity and in_stock bool according to quantity remained once order is created.
        pass

    def calculate_order_payment(self, cart_data: List[Cart]):

        total_price = 0
        for cart in cart_data:
            total_price += cart.product.selling_price * cart.quantity
        return total_price
    
    def sync_order_status_with_line_item_statuses(self):
        
        # syncs order status according to its line items statuses combine.

        line_items = LineItem.objects.filter(order_id=self.order_id)
        for line_item in line_items:
            if line_item.status != LineItem.LineItemStatus.COMPLETED:
                return
        with transaction.atomic():
            Order.objects.select_for_update().filter(id=self.order_id).get().update(status=Order.OrderStatuses.COMPLETED)
        return

    def validate_order(self, cart_data: List[Cart]):

        for cart in cart_data:
            product = cart.product
            if product.in_stock and product.available_quantity >= cart.quantity:
                continue
            else: return False, "Product is currently out of stock"

        total_price = self.calculate_order_payment(cart_data=cart_data)

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    cart_price = total_price,
                    total_price = total_price,
                    status = Order.OrderStatuses.CREATED
                )
                line_items_to_be_created = []

                for cart in cart_data:
                    line_items_to_be_created.append(
                        LineItem(
                            order= order,
                            product_id= cart.product_id,
                            quantity= cart.quantity,
                            status= LineItem.LineItemStatus.CREATED
                        )
                    )
                LineItem.objects.bulk_create(line_items_to_be_created, batch_size=25)

                # create line item metas to keep all order and product related data even if main product instance is updated with selling_price.
                self.create_line_item_metas()

                # Subtract placed orders product inventory and update its in_stock and available_quantity with calculated values.
                self.sync_product_quantity()

                payment_link = PaymentService(order_id=order.id).generate_payment_link_for_order(total_price=total_price)

                return True, payment_link
            
        except Exception as e:
            return False, e
        

    def place_order(self):

        line_items = LineItem.objects.filter(order_id=self.order_id)

        line_item_metas_for_print_books = LineItemMeta.objects.filter(line_item__in=line_items, key=LineItemMeta.LineItemMetaKeys.PRODUCT_CATEGORY_NAME, value= 'PAPER_BOOK')

        line_item_metas_for_e_books = LineItemMeta.objects.filter(line_item__in=line_items, key=LineItemMeta.LineItemMetaKeys.PRODUCT_CATEGORY_NAME, value= 'E_BOOK')

        try:
            with transaction.atomic():

                for line_item_meta in line_item_metas_for_print_books:

                    status, msg = ShipmentService().print_and_ship_line_item(line_item_id=line_item_meta.line_item.id)

                    if status:
                        LineItem.objects.filter(id=line_item_meta.line_item.id).update(status=LineItem.LineItemStatus.PROCESSED)
                    else: continue

                for line_item_meta in  line_item_metas_for_e_books:

                    # Write a task here to send users with link of e-books
                    # Mark LinItem status as Completed as e-book link has been sent to user.
                    LineItem.objects.filter(id=line_item_meta.line_item.id).update(status=LineItem.LineItemStatus.COMPLETED)

                Order.objects.filter(id=self.order_id).update(status=Order.OrderStatuses.PLACED)

                self.sync_order_status_with_line_item_statuses()

                return True, "Order placed successfully."
        except Exception as e:
            return False, str(e)
                











