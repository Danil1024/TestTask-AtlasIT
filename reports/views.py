from pathlib import Path

from celery.result import AsyncResult
from django.conf import settings
from django.http import FileResponse, HttpRequest, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .tasks import generate_customers_report_task, generate_revenue_report_task


# Async views

@csrf_exempt
@require_POST
def revenue_report_async_view(request: HttpRequest) -> JsonResponse:
    task = generate_revenue_report_task.delay()

    return JsonResponse({'task_id': task.id})


@csrf_exempt
@require_POST
def customers_report_async_view(request: HttpRequest) -> JsonResponse:
    task = generate_customers_report_task.delay()
    
    return JsonResponse({'task_id': task.id})


@require_GET
def task_status_view(request: HttpRequest, task_id: str) -> JsonResponse:
    """
    Возвращает текущий статус задачи по task_id.
    
    Возможные статусы:
    - PENDING: задача в очереди, ещё не взята воркером
    - STARTED: воркер начал выполнение
    - SUCCESS: задача завершена успешно
    - FAILURE: задача завершилась с ошибкой
    """
    
    result = AsyncResult(task_id)
    
    response_data = {
        'task_id': task_id,
        'status': result.status,
    }

    if result.successful():
        response_data['result'] = result.result
    
    if result.failed():
        response_data['error'] = str(result.result)
    
    return JsonResponse(response_data)


@require_GET
def download_report_view(request: HttpRequest, task_id: str) -> FileResponse | JsonResponse:
    """
    Отдаёт готовый XLSX по task_id, если задача завершилась успешно.
    """
    result = AsyncResult(task_id)

    if result.state in ('PENDING', 'STARTED'):
        return JsonResponse(
            {'detail': 'Отчёт ещё не готов, проверьте статус через /reports/status/<task_id>/'},
            status=409,
        )

    if result.failed():
        return JsonResponse(
            {'detail': 'Генерация отчёта завершилась с ошибкой', 'error': str(result.result)},
            status=500,
        )

    if not result.successful():
        return JsonResponse({'detail': f'Неожиданный статус задачи: {result.status}'}, status=400)

    raw_path = result.result
    if not isinstance(raw_path, str):
        return JsonResponse({'detail': 'Некорректный результат задачи'}, status=500)

    file_path = Path(raw_path).resolve()
    reports_root = Path(settings.REPORTS_ROOT).resolve()
    try:
        file_path.relative_to(reports_root)
    except ValueError:
        return JsonResponse({'detail': 'Недопустимый путь к файлу'}, status=400)

    if not file_path.is_file():
        return JsonResponse({'detail': 'Файл отчёта не найден на диске'}, status=404)

    return FileResponse(
        file_path.open('rb'),
        as_attachment=True,
        filename=file_path.name,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


# Sync views

from django.http import HttpResponse
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
