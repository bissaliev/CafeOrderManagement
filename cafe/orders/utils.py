from datetime import datetime, timedelta

from django.db.models import Case, DecimalField, F, Q, Sum, When
from django.db.models.expressions import CombinedExpression
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet


def calculate_revenue(queryset: QuerySet) -> dict[str, DecimalField]:
    """
    Вычисляет общую выручку за разные периоды времени
    (всё время, сегодня, неделя, месяц) на основе переданного queryset.
    """
    now = datetime.now()
    today = now.date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    revenue = queryset.aggregate(
        all_time=build_revenue_expression(),
        today=build_revenue_expression(Q(updated__date=today)),
        week=build_revenue_expression(Q(updated__date__gte=start_of_week)),
        month=build_revenue_expression(Q(updated__date__gte=start_of_month)),
    )
    return revenue


def build_revenue_expression(condition: Q | None = None) -> CombinedExpression:
    """
    Строит выражение для подсчёта общей выручки с учётом
    переданного условия фильтрации.
    """

    total_price_expr = F("items__price") * F("items__quantity")
    expr = (
        Case(When(condition, then=total_price_expr))
        if condition
        else total_price_expr
    )
    return Coalesce(Sum(expr), 0, output_field=DecimalField())
