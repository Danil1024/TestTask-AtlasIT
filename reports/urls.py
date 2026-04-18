from django.urls import path
from . import views


urlpatterns = [
    path('revenue/', views.revenue_report_view, name='revenue_report'),
    path('customers/', views.customers_report_view, name='customers_report'),
]
