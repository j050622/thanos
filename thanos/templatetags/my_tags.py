from django.template import Library
from django.utils.safestring import mark_safe
from django.shortcuts import reverse

from thanos.service.crm import site

register = Library()


@register.inclusion_tag('thanos/changelist_table.html')
def show_table(head_list, data_list):
    return {"head_list": head_list, "data_list": data_list}


@register.inclusion_tag('thanos/add_edit_form.html')
def show_form(modelform):
    from django.forms.boundfield import BoundField
    from django.db.models.query import QuerySet
    from django.forms.models import ModelChoiceField, ModelMultipleChoiceField

    new_form = []
    for bound_field in modelform:
        info = {"popUp": False, "bound_field": bound_field}

        field_obj = bound_field.field
        # print(type(field_obj))

        ## 只有符合条件的字段才能有添加按钮，使用popUp
        # 符合条件的字段在ModelForm中表现为ModelChoiceField或其子类，在Model中表现为FK和M2M类
        if isinstance(field_obj, ModelChoiceField):
            rel_class_name = field_obj.queryset.model
            if rel_class_name in site._registry:
                print(rel_class_name)

                popUp_url = ''
                info["popUp"] = True
                info["popUp_url"] = popUp_url
    return {}
