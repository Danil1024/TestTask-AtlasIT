from django.core.management.base import BaseCommand
from django.db import transaction

from datetime import timezone as dt_timezone
from faker import Faker
from tqdm import tqdm
import random

from reports.models import Customer, Order


fake = Faker()
CUSTOMER_COUNT = 3000
ORDER_COUNT = 30000
CUSTOMER_BATCH = 500
ORDER_BATCH = 1000


class Command(BaseCommand):
    help = 'Generate fake data'

    @transaction.atomic
    def handle(self, *args, **options):
        Order.objects.all().delete()
        Customer.objects.all().delete()
        fake.unique.clear()

        customers = [
            Customer(name=fake.name(), email=fake.unique.email())
            for _ in range(CUSTOMER_COUNT)
        ]
        customer_batches = [customers[i:i+CUSTOMER_BATCH] for i in range(0, len(customers), CUSTOMER_BATCH)]
        for batch in tqdm(customer_batches, desc='Creating customers'):
            Customer.objects.bulk_create(batch)

        customer_ids = list(Customer.objects.values_list('id', flat=True))

        orders = [
            Order(
                customer_id=random.choice(customer_ids),
                amount=round(random.uniform(100, 50000), 2),
                status=random.choice(Order.Status.values),
                created_at=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=dt_timezone.utc),
            )
            for _ in range(ORDER_COUNT)
        ]
        order_batches = [orders[i:i+ORDER_BATCH] for i in range(0, len(orders), ORDER_BATCH)]
        for batch in tqdm(order_batches, desc='Creating orders  '):
            Order.objects.bulk_create(batch)
        
        self.stdout.write(self.style.SUCCESS(
            f'Done: {CUSTOMER_COUNT} customers, {ORDER_COUNT} orders'
        ))
