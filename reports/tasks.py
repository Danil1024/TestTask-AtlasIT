from celery import shared_task
from django.conf import settings

from reports.reports import generate_revenue_report, generate_customers_report


@shared_task(bind=True)
def generate_revenue_report_task(self):
    buffer = generate_revenue_report()
    
    file_path = settings.REPORTS_ROOT / f'revenue_{self.request.id}.xlsx'
    settings.REPORTS_ROOT.mkdir(exist_ok=True)
    
    with open(file_path, 'wb') as f:
        f.write(buffer.getvalue())
    
    return str(file_path)


@shared_task(bind=True)
def generate_customers_report_task(self):
    buffer = generate_customers_report()
    
    file_path = settings.REPORTS_ROOT / f'customers_{self.request.id}.xlsx'
    settings.REPORTS_ROOT.mkdir(exist_ok=True)
    
    with open(file_path, 'wb') as f:
        f.write(buffer.getvalue())
    
    return str(file_path)
