from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


@register.inclusion_tag('thanos/temp_table.html')
def show_table(head_list, data_list):
    return {"head_list": head_list, "data_list": data_list}
