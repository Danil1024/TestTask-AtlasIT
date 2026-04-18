from django.http import HttpResponse, HttpRequest
from .reports import generate_revenue_report, generate_customers_report


def revenue_report_view(request: HttpRequest) -> HttpResponse:
    buffer = generate_revenue_report()
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="revenue_report.xlsx"'
    return response


def customers_report_view(request: HttpRequest) -> HttpResponse:
    buffer = generate_customers_report()
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="customers_report.xlsx"'
    return response
