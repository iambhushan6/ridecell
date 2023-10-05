import requests
from main.models import Cart, Product, ProductCategory, PaymentRequest, Shipment, Order, LineItem, LineItemMeta
from main.order import OrderService
from django.db import transaction

class ShipmentService:

    def __init__(self) -> None:
        pass

    def print_and_ship_line_item(self, line_item_id: int):

        line_item_instance = LineItem.objects.filter(id=line_item_id).select_related('order','user').first()
        user_address = line_item_instance.order.user.address
        book_name = LineItemMeta.objects.filter(line_item_id=line_item_id, key=LineItemMeta.LineItemMetaKeys.PRODUCT_NAME).first()
        quantity = LineItemMeta.objects.filter(line_item_id=line_item_id, key=LineItemMeta.LineItemMetaKeys.PRODUCT_QUANTITY).first()

        shipment = Shipment.objects.create(
            order= line_item_instance.order,
            line_item_id= line_item_id,
            status= Shipment.ShipmentStatuses.SHIPPED
        )
        try:
            # send this payload in request for print and shipping at 3p
            payload = {
                "user_address" : user_address, 
                "book_name" : book_name,
                "quantity" : quantity
            }
            third_party_shipment_identifier = '123465789'
            # When book print/shipment request is placed print/shipment carrier will return a unique identifier of request which will be used for trancking and identification.
        except Exception as e:
            return False, e
        
        # Update Shipment instance with third party identifier
        Shipment.objects.filter(id=shipment.id).update(third_party_identifier=third_party_shipment_identifier)
        
        return True, "shipment created successfully at 3p"
    
    def sync_shipment_status_with_3p(self, shipment_id:int):

        try:
            shipment = Shipment.objects.filter(id=shipment_id).first()
            line_item = shipment.line_item

            if shipment:
                response = requests.get(f"https://3p-status-traking-link/?identifier={shipment.third_party_identifier}")

                data = response.json()
                status = None
                if data["status"] == Shipment.ShipmentStatuses.PRINTED:
                    status = Shipment.ShipmentStatuses.PRINTED
                elif data["status"] == Shipment.ShipmentStatuses.IN_TRANSIT:
                    status = Shipment.ShipmentStatuses.IN_TRANSIT
                elif data["status"] == Shipment.ShipmentStatuses.DELIVERED:
                    status = Shipment.ShipmentStatuses.DELIVERED
                elif data["status"] == Shipment.ShipmentStatuses.FAILED:
                    status = Shipment.ShipmentStatuses.FAILED

                with transaction.atomic():

                    if status:
                        shipment.status = status
                        shipment.save()

                    if status == Shipment.ShipmentStatuses.DELIVERED:
                        
                        # sync line item status with shipment status and with order respectively.
                        line_item.status = LineItem.LineItemStatus.COMPLETED
                        line_item.save()
                        OrderService(order_id=shipment.order_id).sync_order_status_with_line_item_statuses()

                    return True, "shipment status synced with third party"
            else: return False

        except Exception as e:
            return False
        