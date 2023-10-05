from main.models import Cart, Product, ProductCategory, PaymentRequest, Shipment, Order, LineItem, LineItemMeta



class PaymentService:

    def __init__(self, order_id: int) -> None:
        self.order_id = order_id

    def generate_payment_link_for_order(self, total_price:int):

        payment_request = PaymentRequest.objects.create(
            order_id= self.order_id,
            total_price= total_price,
            status= PaymentRequest.PaymentRequestStatus.CREATED
        )
        try:
            payment_link = '3rd party api call to payment mediator with given total price'
            # send order_id in payload to identify for which order payment was done when payment is paid and 3rd party send us a webhook of successful payment.
        except Exception as e:
            return False, e
        
        PaymentRequest.objects.filter(id=payment_request.id).update(status=PaymentRequest.PaymentRequestStatus.PROCESSED)
        
        return True, payment_link