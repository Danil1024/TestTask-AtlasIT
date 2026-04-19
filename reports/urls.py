from django.urls import path

from . import views


urlpatterns = [
    # Async views - обработка в фоне (не блокирующая)
    path('revenue_async/', views.revenue_report_async_view, name='revenue_report_async'),
    path('customers_async/', views.customers_report_async_view, name='customers_report_async'),
    path('status/<str:task_id>/', views.task_status_view, name='task_status'),
    path('download/<str:task_id>/', views.download_report_view, name='download_report'),

    # Sync views — обработка в рамках HTTP-запроса (блокирующая)
    path('revenue/', views.revenue_report_view, name='revenue_report'),
    path('customers/', views.customers_report_view, name='customers_report'),
]
