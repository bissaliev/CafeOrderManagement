from django.template.library import Library

register = Library()


@register.filter
def addclass(tag, css):
    return tag.as_widget(attrs={"class": css})
