from datetime import datetime


def year(request):
    current_datetime = datetime.now()
    """Добавляет переменную с текущим годом."""
    return {
        'year': current_datetime.year,
    }
