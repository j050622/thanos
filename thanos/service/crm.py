import json

from django.shortcuts import render, redirect, reverse, HttpResponse
from django.utils.safestring import mark_safe
from django.conf.urls import url, include
from django.forms import ModelForm
from django.http import JsonResponse, QueryDict
from django.db.models import Q

from .paginator import Paginator


class ChangeList:
    """构造changelist类"""

    def __init__(self, config_obj, obj_list, pager_params):
        # 配置信息
        self.list_display = config_obj.get_list_display()
        self.show_add_btn = config_obj.get_show_add_btn()
        self.show_search_form = config_obj.get_show_search_form()
        self.search_input_name = config_obj.search_input_name
        self.list_per_page = config_obj.list_per_page

        # 基本属性
        self.config_obj = config_obj
        self.request = config_obj.request
        self.model_class = config_obj.model_class
        self.model_name = config_obj.model_class._meta.model_name
        self.add_url = config_obj.ele_add()

        ### 分页操作 ###
        try:
            current_page_num = int(self.request.GET.get('page', 1))
        except TypeError:
            current_page_num = 1

        paginator = Paginator(pager_params, obj_list, current_page_num, self.request.path, self.list_per_page)
        self.show_obj_list = paginator.show_obj_list()
        self.pager_html = paginator.pager_html()

    def head_list(self):
        """处理表头信息"""

        def header(self):
            if not self.list_display:  # 如果没有自定义list_display
                yield self.model_class._meta.model_name.upper()

            for field_name in self.list_display:
                if isinstance(field_name, str):
                    verbose_name = self.model_class._meta.get_field(field_name).verbose_name
                else:
                    verbose_name = field_name(is_header=True)
                yield verbose_name

        return header(self)

    def data_list(self):
        """处理数据部分"""

        def data(self):
            for obj in self.show_obj_list:
                if not self.list_display:  # 如果没有自定义list_display
                    yield [obj]

                def inner(self, obj):
                    for field_name in self.list_display:
                        if isinstance(field_name, str):
                            val = getattr(obj, field_name)
                        else:
                            val = field_name(obj)
                        yield val

                yield inner(self, obj)

        return data(self)


class CrmConfig:
    """对传入的Model表名，分配‘增删改查’等的URL"""

    ###### 初始化 ######
    def __init__(self, model_class, site_obj):
        self.model_class = model_class
        self.model_name = model_class._meta.model_name
        self.site_obj = site_obj
        self.app_label = self.model_class._meta.app_label
        self.request = None
        self.query_dict_key = '_next'

    ###### 基本配置 ######
    list_display = []  # 要在列表页面显示的列
    show_add_btn = False  # 默认不显示添加按钮
    show_search_form = False
    search_fields = []
    search_input_name = '_q'
    model_form_class = None  # 在派生类里指定ModelForm
    list_per_page = 10

    def get_show_add_btn(self):
        # 根据权限，设置是否显示“添加”按钮
        return self.show_add_btn

    def get_show_search_form(self):
        """设置是否显示搜索框组"""
        return self.show_search_form

    def get_search_fields(self):
        """要搜索的字段"""
        return self.search_fields

    # 反向解析URL #
    def get_changelist_url(self):
        url_verbose_name = '%s_%s_changelist' % (self.app_label, self.model_name)
        return reverse(url_verbose_name)

    def get_add_url(self):
        url_verbose_name = '%s_%s_add' % (self.app_label, self.model_name)
        return reverse(url_verbose_name)

    def get_change_url(self, nid):
        url_verbose_name = '%s_%s_change' % (self.app_label, self.model_name)
        return reverse(url_verbose_name, args=(nid,))

    def get_delete_url(self, nid):
        url_verbose_name = '%s_%s_delete' % (self.app_label, self.model_name)
        return reverse(url_verbose_name, args=(nid,))

    # 列表页面的多选框、编辑、删除，动态填充<a>标签的href属性 #
    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return mark_safe('<input type="checkbox" name="obj_list" value="###">')
        return mark_safe('<input type="checkbox" name="obj" value="%s">' % obj.id)

    def ele_add(self):
        if self.request.GET:
            params_dict = QueryDict(mutable=True)
            params_dict[self.query_dict_key] = self.request.GET.urlencode()
            return '%s?%s' % (self.get_add_url(), params_dict.urlencode())
        else:
            return '%s' % self.get_add_url()

    def ele_change(self, obj=None, is_header=False):
        if is_header:
            return '修改'

        if self.request.GET:
            params_dict = QueryDict(mutable=True)
            params_dict[self.query_dict_key] = self.request.GET.urlencode()
            return mark_safe('<a href="%s?%s">修改</a>' % (self.get_change_url(obj.id), params_dict.urlencode()))
        else:
            return mark_safe('<a href="%s">修改</a>' % self.get_change_url(obj.id))

    def ele_delete(self, obj=None, is_header=False):
        if is_header:
            return '删除'

        if self.request.GET:
            params_dict = QueryDict(mutable=True)
            params_dict[self.query_dict_key] = self.request.GET.urlencode()
            return mark_safe('<a href="%s?%s">删除</a>' % (self.get_delete_url(obj.id), params_dict.urlencode()))
        else:
            return mark_safe('<a href="%s">删除</a>' % self.get_delete_url(obj.id))

    # 在默认的list_display中添加checkbox、change、delete方法 #
    def get_list_display(self):
        data = []
        if self.list_display:
            data.extend(self.list_display)

            data.insert(0, self.checkbox)
            data.append(self.ele_change)
            data.append(self.ele_delete)

        return data

    ###### 增删改查URL分发 ######
    def get_urls(self):

        def wrap(view):
            def inner(request, *args, **kwargs):
                self.request = request
                return view(request, *args, **kwargs)

            return inner

        info = self.app_label, self.model_name

        urlpatterns = [
            url(r'^$', wrap(self.changelist_view), name='%s_%s_changelist' % info),
            url(r'^add/$', wrap(self.add_view), name='%s_%s_add' % info),
            url(r'^(\d+)/delete$', wrap(self.delete_view), name='%s_%s_delete' % info),
            url(r'^(\d+)/change$', wrap(self.change_view), name='%s_%s_change' % info),
        ]
        urlpatterns.extend(self.extra_urls())

        return urlpatterns

    ### 在get_urls()的基础上自定义其他URL，在派生类中重写 ###
    def extra_urls(self):
        return []

    @property
    def urls(self):
        return self.get_urls()

    def get_model_form_class(self):
        """动态生成ModelForm"""
        if self.model_form_class:
            return self.model_form_class

        class PrototypeModelForm(ModelForm):
            class Meta:
                model = self.model_class
                fields = '__all__'

        return PrototypeModelForm

    ###### 增删改查URL对应的视图函数 ######

    def changelist_view(self, request, *args, **kwargs):
        ### 生成最终匹配条件，获取QuerySet ###
        kew_word = request.GET.get(self.search_input_name)

        condition = Q()
        condition1 = Q()
        condition2 = Q()
        pager_params = QueryDict(mutable=True)

        condition1.connector = 'OR'
        if kew_word:
            for field in self.get_search_fields():
                if 'id' in field:
                    if kew_word.isnumeric():
                        condition1.children.append((field, kew_word))
                else:
                    condition1.children.append((field, kew_word))

        for field, value in request.GET.items():
            if field != 'page':
                pager_params[field] = value
                if field != self.search_input_name:
                    condition2.children.append((field, value))

        condition.add(condition1, 'AND')
        condition.add(condition2, 'AND')

        obj_list = self.model_class.objects.filter(condition)  # 根据条件查询数据库

        ### 实例化ChangeList对象 ###
        cl = ChangeList(self, obj_list, pager_params)  # 传入当前对象

        return render(request, 'thanos/changelist_view.html', {"cl": cl})

    def add_view(self, request, *args, **kwargs):
        model_form = self.get_model_form_class()
        if request.method == 'GET':
            add_edit_form = model_form()
            return render(request, 'thanos/add_view.html',
                          {"model_name": self.model_name, "add_edit_form": add_edit_form})
        else:
            add_edit_form = model_form(data=request.POST)
            if not add_edit_form.is_valid():
                return render(request, 'thanos/add_view.html',
                              {"model_name": self.model_name, "add_edit_form": add_edit_form})
            else:
                add_edit_form.save()
            if request.GET:
                return redirect('%s?%s' % (self.get_changelist_url(), request.GET.get(self.query_dict_key)))
            else:
                return redirect('%s' % self.get_changelist_url())

    def delete_view(self, request, nid, *args, **kwargs):
        if request.method == 'GET':
            return render(request, 'thanos/delete_view.html')
        else:
            opt = json.loads(request.body.decode()).get('opt')
            res_dict = {"status": True, "error_msg": None, "rtn_url": None}
            try:
                if opt == '确定':
                    self.model_class.objects.filter(pk=nid).delete()
                if request.GET:
                    res_dict['rtn_url'] = '%s?%s' % (self.get_changelist_url(), request.GET.get(self.query_dict_key))
                else:
                    res_dict['rtn_url'] = '%s' % self.get_changelist_url()


            except Exception as e:
                res_dict['status'] = False
                res_dict['error_msg'] = str(e)

            return JsonResponse(res_dict)

    def change_view(self, request, nid, *args, **kwargs):
        model_form = self.get_model_form_class()
        current_obj = self.model_class.objects.filter(pk=nid).first()
        if not current_obj:
            return redirect(self.get_changelist_url())

        if request.method == 'GET':
            add_edit_form = model_form(instance=current_obj)
            return render(request, 'thanos/edit_view.html',
                          {"model_name": self.model_name, "add_edit_form": add_edit_form})
        else:
            add_edit_form = model_form(instance=current_obj, data=request.POST)
            add_edit_form.save()
            if request.GET:
                return redirect('%s?%s' % (self.get_changelist_url(), request.GET.get(self.query_dict_key)))
            else:
                return redirect('%s' % self.get_changelist_url())


class CrmSite:
    '''用于分发CRM下的基础URL，并遍历所有注册的类，获取每个类对应的表下的增删改查等URl'''

    def __init__(self):
        self._registry = {}

    def register(self, model_class, config_class=None):
        if not config_class:
            config_class = CrmConfig
        self._registry[model_class] = config_class(model_class, self)

    def get_urls(self):
        urlpatterns = []
        app_labels_list = []
        for model, config_obj in self._registry.items():
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            urlpatterns += [url(r'^%s/%s/' % (app_label, model_name), include(config_obj.urls, None, None))]

            ######待整理######
            # if app_label not in app_labels_list:
            #     app_labels_list.append(app_label)
            ######

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), None, None


site = CrmSite()
