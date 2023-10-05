from celery import shared_task
from main.shipment import ShipmentService
from main.models import Shipment, LineItem, Order
from datetime import datetime, timedelta


@shared_task(bind=True)
def scheduled_task_sync_shipment_statuses_with_third_party(self):

    # Choose only those shipments whose status can be updated i.e a non terminating status
    status_list = [
        Shipment.ShipmentStatuses.SHIPPED ,
        Shipment.ShipmentStatuses.PRINTED ,
        Shipment.ShipmentStatuses.IN_TRANSIT ,
        Shipment.ShipmentStatuses.OUT_FOR_DELIVERY
    ]

    shipments = Shipment.objects.filter(
        status__in=status_list,
        created_at__gte=datetime.now() - timedelta(days=30),
    )

    for shipment in shipments:
        ShipmentService().sync_shipment_status_with_3p(shipment_id=shipment.id)

    return