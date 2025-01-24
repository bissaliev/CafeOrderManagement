from django.forms.boundfield import BoundField
from django.http import QueryDict
from django.template.context import RequestContext
from django.template.library import Library

register = Library()


@register.filter
def addclass(field: BoundField, css: str):
    """Добавление CSS-класса тегу"""
    return field.as_widget(attrs={"class": css})


@register.simple_tag(takes_context=True)
def get_query(context: RequestContext):
    """Получение QueryString из запроса для корректной работы пагинации"""
    query_string: QueryDict = context["request"].GET.copy()
    if "page" in query_string:
        query_string.pop("page")
    return query_string.urlencode()
