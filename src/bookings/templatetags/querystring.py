from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def sort_url(context, value):
    request = context["request"]
    params = request.GET.copy()
    params["ordering"] = value
    return "?" + params.urlencode()
