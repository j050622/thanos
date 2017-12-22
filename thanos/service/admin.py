import json
import copy

from django.shortcuts import render, redirect, reverse
from django.utils.safestring import mark_safe
from django.conf.urls import url, include
from django.forms import ModelForm
from django.http import JsonResponse, QueryDict
from django.db.models import Q, ForeignKey, ManyToManyField, IntegerField

from .paginator import Paginator


class FilterRowOption:
    def __init__(self, field_name, is_multiple=False, condition=None, is_choice=False):
        self.field_name = field_name
        self.is_multiple = is_multiple
        self.condition = condition
        self.is_choice = is_choice

    def get_queryset(self, _field):
        """获取FK和M2M字段所关联的表的所有记录"""
        if self.condition:
            return _field.rel.to.objects.filter(self.condition)

        return _field.rel.to.objects.all()

    def get_choices(self, _field):
        """获取字段的所有choices选项"""
        return _field.choices


class FilterRow:
    """把组合搜索的每一行（字段下的数据）封装成对象"""

    def __init__(self, row_option, data, request):
        self.data = data
        self.row_option = row_option
        self.request = request
        self.params = copy.deepcopy(request.GET)
        self.params._mutable = True

    def __iter__(self):
        field_name = self.row_option.field_name
        current_pk = self.request.GET.get(field_name)

        ## 生成“全部”按钮
        # 选中的“全部”按钮添加.active，并且点击无效
        if not current_pk:
            yield mark_safe('<button class="btn btn-primary">全部</button>')
            origin_pk_list = []
        else:
            origin_pk_list = self.params.pop(field_name)
            url = '%s?%s' % (self.request.path, self.params.urlencode())
            yield mark_safe('<a class="btn" href="{}">全部</a>'.format(url))

        ## 生成普通按钮
        for val in self.data:
            if self.row_option.is_choice:
                pk, text = val
            else:
                pk, text = str(val.pk), str(val)

            # 搜索条件拼接
            if not self.row_option.is_multiple:
                # 单选
                if current_pk == pk:
                    ele_html = mark_safe('<button class="btn btn-primary">{}</button>'.format(text))
                else:
                    self.params[field_name] = pk
                    url = '%s?%s' % (self.request.path, self.params.urlencode())
                    ele_html = mark_safe('<a class="btn" href="{}">{}</a>'.format(url, text))
            else:
                # 多选
                url_pk_list = copy.deepcopy(origin_pk_list)
                # [1,2]

                if pk in url_pk_list:
                    url_pk_list.remove(pk)  # 点击取消
                    self.params.setlist(field_name, url_pk_list)
                    url = '%s?%s' % (self.request.path, self.params.urlencode())
                    ele_html = mark_safe('<a class="btn btn-primary" href="{}">{}</a>'.format(url, text))
                else:
                    url_pk_list.append(pk)

                    self.params.setlist(field_name, url_pk_list)
                    url = '%s?%s' % (self.request.path, self.params.urlencode())
                    ele_html = mark_safe('<a class="btn" href="{}">{}</a>'.format(url, text))

            yield ele_html


class ChangeList:
    """
    构造changelist类
    """

    def __init__(self, config_obj, obj_list, pager_params):
        # 配置信息
        self.list_display = config_obj.get_list_display()
        self.show_add_btn = config_obj.get_show_add_btn()
        self.show_search_form = config_obj.get_show_search_form()
        self.search_input_name = config_obj.search_input_name
        self.list_per_page = config_obj.list_per_page
        self.actions = config_obj.get_actions()
        self.show_actions = config_obj.get_show_actions()
        self.comb_filter_rows = config_obj.get_comb_filter_rows()

        # 基本属性
        self.config_obj = config_obj
        self.request = config_obj.request
        self.model_class = config_obj.model_class
        self.model_name = config_obj.model_class._meta.model_name
        self.add_href = config_obj.ele_add_href()
        self.search_input_val = config_obj.request.GET.get(config_obj.search_input_name, '')

        ### 分页操作 ###
        try:
            current_page_num = int(self.request.GET.get('page', 1))
        except TypeError:
            current_page_num = 1

        paginator = Paginator(pager_params, obj_list, current_page_num, self.request.path, self.list_per_page)
        self.show_obj_list = paginator.show_obj_list()
        self.pager_html = paginator.pager_html()

    def modify_actions(self):
        """ 加工actions里的函数，用于在前端显示 """
        result = []
        for func in self.actions:
            tmp = {"func_name": func.__name__, "text": func.short_desc}
            result.append(tmp)

        return result

    def head_list(self):
        """ 处理表头信息 """

        def header(self):
            ''' 生成器 '''
            if not self.list_display:  # 如果没有自定义list_display
                yield self.model_class._meta.model_name.upper()

            for field_name in self.list_display:
                if isinstance(field_name, str):
                    verbose_name = self.model_class._meta.get_field(field_name).verbose_name
                else:
                    verbose_name = field_name(self.config_obj, is_header=True)

                yield verbose_name

        return header(self)

    def data_list(self):
        """ 处理表格主体部分 """

        def data(self):
            ''' 生成器 '''
            for obj in self.show_obj_list:
                if not self.list_display:  # 如果没有自定义list_display
                    yield [obj]

                def inner(self, obj):
                    ''' 嵌套生成器 '''
                    for field_name in self.list_display:
                        if isinstance(field_name, str):
                            val = getattr(obj, field_name)
                        else:
                            val = field_name(self.config_obj, obj)
                        yield val

                yield inner(self, obj)

        return data(self)

    def gen_comb_filter(self):
        """组合筛选函数，是一个生成器"""

        for row_option in self.comb_filter_rows:
            _field = self.model_class._meta.get_field(row_option.field_name)
            if isinstance(_field, ForeignKey):
                row = FilterRow(row_option, row_option.get_queryset(_field), self.request)  # django2.0里，.rel.to要用.model
            elif isinstance(_field, ManyToManyField):
                row = FilterRow(row_option, row_option.get_queryset(_field), self.request)
            else:
                # choices类型
                row = FilterRow(row_option, row_option.get_choices(_field), self.request)

            yield row


class CrmConfig:
    """
    对传入的Model表名，分配‘增删改查’等的URL
    """

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
    model_form_class = None  # 在派生类里指定自定义的ModelForm
    list_per_page = 10
    actions = []
    show_actions = False
    comb_filter_rows = []

    def get_show_add_btn(self):
        """ 根据权限，设置是否显示“添加”按钮 """
        return self.show_add_btn

    def get_show_search_form(self):
        """ 设置是否显示搜索框组 """
        return self.show_search_form

    def get_search_fields(self):
        """ 要搜索的字段 """
        return self.search_fields

    def get_actions(self):
        """ 获取actions里的函数名 """
        result = []
        if self.actions:
            result.extend(self.actions)
        return self.actions

    def get_show_actions(self):
        """设置是否显示actions栏（批量操作）"""
        return self.show_actions

    def get_comb_filter_rows(self):
        """ 获取要进行组合筛选的字段 """
        result = []
        if self.comb_filter_rows:
            result.extend(self.comb_filter_rows)
        return result

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

    # 列表页面的多选框、添加、编辑、删除标签，动态填充<a>标签的href属性 #
    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return mark_safe('<input type="checkbox" id="checkbox">')
        return mark_safe('<input type="checkbox" name="obj_id" value="%s">' % obj.id)

    def ele_add_href(self):
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
        """ changelist页面要显示的列 """
        result = []
        if self.list_display:
            result.extend(self.list_display)

            result.insert(0, CrmConfig.checkbox)
            result.append(CrmConfig.ele_change)
            result.append(CrmConfig.ele_delete)

        return result

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

    def extra_urls(self):
        """ 在get_urls()的基础上自定义其他URL，在派生类中重写 """
        return []

    @property
    def urls(self):
        return self.get_urls()

    ###### 增删改查URL对应的视图函数及其附属函数 ######

    def get_search_condition(self):
        """
        从URL和搜索框中获取数据库的筛选条件；
        生成用于保留搜索条件的参数
        """
        kew_word = self.request.GET.get(self.search_input_name)

        condition1 = Q()  # 搜索框条件
        condition2 = Q()  # 地址栏的条件
        condition = Q()  # 最终条件

        pager_params = QueryDict(mutable=True)

        # 搜索框
        condition1.connector = 'OR'
        if kew_word:
            for field in self.get_search_fields():
                is_not_str = isinstance(self.model_class._meta.get_field(field.split('__')[0]),
                                        (ForeignKey, ManyToManyField, IntegerField))
                if is_not_str:
                    # 如果搜索条件的字段不是CharField等字符串类型，则不允许跟字符串进行大小比较
                    if kew_word.isnumeric():
                        condition1.children.append((field, kew_word))
                else:
                    condition1.children.append((field, kew_word))

        # URL中的搜索条件
        for field in self.request.GET.keys():
            value_list = self.request.GET.getlist(field)
            if field != 'page':
                pager_params.setlist(field, value_list)
                if field != self.search_input_name:
                    # 搜索框的关键字要过滤掉
                    condition2.children.append(('%s__in' % field, value_list))

        condition.add(condition1, 'AND')
        condition.add(condition2, 'AND')
        return pager_params, condition

    def changelist_view(self, request, *args, **kwargs):
        """
        展示记录
        """
        if request.method == 'GET':
            pager_params, condition = self.get_search_condition()
            obj_list = self.model_class.objects.filter(condition).distinct()  # 根据条件查询数据库

            ### 实例化ChangeList对象 ###
            cl = ChangeList(self, obj_list, pager_params)  # 传入当前对象

            return render(request, 'thanos/changelist_view.html', {"cl": cl})
        else:
            # actions
            action_func = getattr(self, request.POST.get('action'))
            ret = action_func(request)
            if ret:
                return ret

            return redirect(request.get_full_path())

    def get_model_form_class(self):
        """
        动态生成ModelForm，用于添加、编辑页面生成Form表单
        """
        if self.model_form_class:
            return self.model_form_class

        class PrototypeModelForm(ModelForm):
            class Meta:
                model = self.model_class
                fields = '__all__'

        return PrototypeModelForm

    def add_view(self, request, *args, **kwargs):
        """
        添加记录
        """
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
        """
        删除记录
        """
        if not request.is_ajax():
            return render(request, 'thanos/delete_view.html')
        else:
            opt = request.GET.get('opt')

            res_dict = {"status": True, "error_msg": None, "rtn_url": None}
            try:
                if opt == '确定':
                    self.model_class.objects.filter(pk=nid).delete()

                next_to = request.GET.get(self.query_dict_key)
                if next_to:
                    res_dict['rtn_url'] = '%s?%s' % (self.get_changelist_url(), next_to)
                else:
                    res_dict['rtn_url'] = '%s' % self.get_changelist_url()

            except Exception as e:
                res_dict['status'] = False
                res_dict['error_msg'] = str(e)

            return JsonResponse(res_dict)

    def change_view(self, request, nid, *args, **kwargs):
        """
        修改记录
        """
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
