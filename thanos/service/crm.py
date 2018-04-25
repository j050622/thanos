import json
import copy

from django.shortcuts import render, redirect, reverse, HttpResponse
from django.utils.safestring import mark_safe
from django.conf.urls import url, include
from django.forms import ModelForm
from django.http import JsonResponse, QueryDict
from django.db.models import Q, ForeignKey, ManyToManyField, IntegerField

from .paginator import Paginator


class FilterRowOption:
    """
    
    """

    def __init__(self, field_name, is_multiple=False, condition=None, is_choice=False, func_get_val=None):
        """
        :param field_name:要生成一行搜索条件的来源字段
        :param is_multiple:设置是否多选
        :param condition:必须是一个字典，用于存放查询条件
        :param is_choice:
            如果当前字段的取值范围定义在model表的xx_choices字段中，这里应该设置为True
        :param func_get_val:
            <a>标签中有的参数需要对应路由规则中的正则表达式，这里的函数用于生成这些参数
        """
        self.field_name = field_name
        self.is_multiple = is_multiple
        self.condition = condition
        self.is_choice = is_choice
        self.func_get_val = func_get_val

    def get_queryset(self, _field):
        """获取FK和M2M字段所关联的表的所有记录"""
        if self.condition:
            return _field.rel.to.objects.filter(**self.condition)
        else:
            return _field.rel.to.objects.all()

    def get_choices(self, _field):
        """获取字段的所有choices选项"""
        return _field.choices


class FilterRow:
    """把组合搜索的每一行（字段下的数据）封装成对象"""

    def __init__(self, row_option, queryset_or_choices, request):
        self.queryset_or_choices = queryset_or_choices
        self.row_option = row_option
        self.request = request
        self.params = copy.deepcopy(request.GET)
        self.params._mutable = True

    def __iter__(self):
        field_name = self.row_option.field_name
        current_val = self.request.GET.get(field_name)

        ## 生成“全部”按钮
        # 选中的“全部”按钮添加，并且点击无效
        if not current_val:
            origin_val_list = []
            yield mark_safe('<button class="btn btn-primary">全部</button>')
        else:
            origin_val_list = self.params.pop(field_name)
            url = '%s?%s' % (self.request.path, self.params.urlencode())
            yield mark_safe('<a class="btn" href="{}">全部</a>'.format(url))

        ## 生成普通按钮
        for tuple_or_obj in self.queryset_or_choices:
            if self.row_option.is_choice:
                tuple0 = tuple_or_obj
                val, text = str(tuple0[0]), tuple0[1]
            else:
                obj = tuple_or_obj
                tmp_func = self.row_option.func_get_val
                val = tmp_func(obj) if tmp_func else str(obj.pk)
                text = str(obj)

            # 搜索条件拼接
            if not self.row_option.is_multiple:
                # 单选
                if current_val == val:
                    ele_html = mark_safe('<button class="btn btn-primary">{}</button>'.format(text))
                else:
                    self.params[field_name] = val
                    url = '%s?%s' % (self.request.path, self.params.urlencode())
                    ele_html = mark_safe('<a class="btn" href="{}">{}</a>'.format(url, text))
            else:
                # 多选
                url_val_list = copy.deepcopy(origin_val_list)  # [1002,1003,1004,1000]

                if val in url_val_list:
                    url_val_list.remove(val)  # 点击取消
                    self.params.setlist(field_name, url_val_list)
                    url = '%s?%s' % (self.request.path, self.params.urlencode())
                    ele_html = mark_safe('<a class="btn btn-primary" href="{}">{}</a>'.format(url, text))
                else:
                    url_val_list.append(val)

                    self.params.setlist(field_name, url_val_list)
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
        self.list_editable = config_obj.get_list_editable()
        self.show_add_btn = config_obj.get_show_add_btn()
        self.show_search_form = config_obj.get_show_search_form()
        self.search_input_name = config_obj.search_input_name
        self.list_per_page = config_obj.list_per_page
        self.actions_funcs = config_obj.get_actions_funcs()
        self.show_actions = config_obj.get_show_actions()
        self.comb_filter_rows = config_obj.get_comb_filter_rows()
        self.show_comb_filter = config_obj.get_show_comb_filter()
        self.query_dict_key = config_obj.query_dict_key

        # 基本属性
        self.config_obj = config_obj
        self.request = config_obj.request
        self.model_class = config_obj.model_class
        self.model_name = config_obj.model_name
        self.app_label = config_obj.app_label
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
        for func in self.actions_funcs:
            tmp_dict = {"func_name": func.__name__, "text": func.short_desc}
            result.append(tmp_dict)

        return result

    def head_list(self):
        """ 处理表头信息 """

        def header(self):
            ''' 生成器 '''
            if not self.list_display:  # 如果没有自定义list_display
                yield self.model_name.upper()

            for field_or_func in self.list_display:
                if isinstance(field_or_func, str):
                    verbose_name = self.model_class._meta.get_field(field_or_func).verbose_name
                else:
                    verbose_name = field_or_func(self.config_obj, is_header=True)

                yield verbose_name

        return header(self)

    def data_list(self):
        """ 处理表格主体部分 """

        def data(self):
            ''' 生成器 '''

            for obj in self.show_obj_list:

                if not self.list_display:
                    edit_url = reverse('%s_%s_change' % (self.app_label, self.model_name), args=(obj.id,))
                    yield [mark_safe('<a href="{}">{}</a>'.format(edit_url, str(obj)))]

                def inner(self, obj):
                    ''' 嵌套生成器 '''
                    for field_or_func in self.list_display:
                        if isinstance(field_or_func, str):
                            val = getattr(obj, field_or_func)
                        else:
                            val = field_or_func(self.config_obj, obj)

                        if field_or_func in self.list_editable:
                            edit_url = reverse('%s_%s_change' % (self.app_label, self.model_name), args=(obj.id,))
                            if self.request.GET:
                                params_dict = QueryDict(mutable=True)
                                params_dict[self.query_dict_key] = self.request.GET.urlencode()
                                val = mark_safe('<a href="{}?{}">{}</a>'.format(edit_url, params_dict.urlencode(), val))
                            else:
                                val = mark_safe('<a href="{}">{}</a>'.format(edit_url, val))

                        yield val

                yield inner(self, obj)

        return data(self)

    def gen_comb_filter(self):
        """组合筛选函数，是一个生成器"""

        for row_option in self.comb_filter_rows:
            _field = self.model_class._meta.get_field(row_option.field_name)
            if isinstance(_field, ForeignKey):
                row = FilterRow(row_option, row_option.get_queryset(_field), self.request)
            elif isinstance(_field, ManyToManyField):
                row = FilterRow(row_option, row_option.get_queryset(_field), self.request)
            else:
                # choices类型
                row = FilterRow(row_option, row_option.get_choices(_field), self.request)

            yield row


class CrmConfig:
    """
    对传入的Model表名，分配‘增删改查’等的URL及其对应的视图函数
    可以对相应页面的显示进行配置
    """

    def __init__(self, model_class, site_obj):
        self.model_class = model_class
        self.site_obj = site_obj

        self.model_name = model_class._meta.model_name
        self.app_label = model_class._meta.app_label
        self.request = None
        self.query_dict_key = '_next'
        self.search_input_name = '_q'

    ###### 基本配置 ######
    list_display = []  # 要在列表页面显示的列
    list_editable = []  # 供点击进入编辑页面的字段
    order_by_condition = []  # 排序条件
    show_add_btn = True  # 默认不显示添加按钮
    show_search_form = False
    search_fields = []  # 供搜索的字段
    model_form_class = None  # 在派生类里指定自定义的ModelForm
    list_per_page = 10
    actions_funcs = []  # 批量操作的函数
    show_actions = False
    comb_filter_rows = []  # 供组合搜索的字段
    show_comb_filter = False

    def get_list_editable(self):
        result = []
        if self.list_editable:
            result.extend(self.list_editable)
        return result

    def get_order_by_condition(self):
        result = []
        if self.order_by_condition:
            result.extend(self.order_by_condition)
        return result

    def get_show_add_btn(self):
        """ 根据权限，设置是否显示“添加”按钮 """
        return self.show_add_btn

    def get_show_search_form(self):
        """ 设置是否显示搜索框组 """
        return self.show_search_form

    def get_search_fields(self):
        """ 要搜索的字段 """
        return self.search_fields

    def get_actions_funcs(self):
        """ 获取actions里的函数名 """
        result = []
        if self.actions_funcs:
            result.extend(self.actions_funcs)
        return result

    def get_show_actions(self):
        """设置是否显示actions栏（批量操作）"""
        return self.show_actions

    def get_comb_filter_rows(self):
        """ 获取要进行组合筛选的字段 """
        result = []
        if self.comb_filter_rows:
            result.extend(self.comb_filter_rows)
        return result

    def get_show_comb_filter(self):
        """设置是否显示组合搜索栏"""
        return self.show_comb_filter

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
        return mark_safe('<input type="checkbox" name="pk" value="%s">' % obj.pk)

    def ele_add_href(self):
        """
        由于添加按钮需要在前端指定样式，所以这里值生成href属性，不直接生成<a>标签
        """
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
            # result.append(CrmConfig.ele_change)
            result.append(CrmConfig.ele_delete)

        return result

    ###### 增删改查URL分发 ######
    def wrap(self, view):
        def inner(request, *args, **kwargs):
            self.request = request
            return view(request, *args, **kwargs)

        return inner

    def get_urls(self):
        info = self.app_label, self.model_name
        urlpatterns = [
            url(r'^$', self.wrap(self.changelist_view), name='%s_%s_changelist' % info),
            url(r'^add/$', self.wrap(self.add_view), name='%s_%s_add' % info),
            url(r'^(\d+)/delete/$', self.wrap(self.delete_view), name='%s_%s_delete' % info),
            url(r'^(\d+)/change/$', self.wrap(self.change_view), name='%s_%s_change' % info),
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

        pager_params = QueryDict(mutable=True)

        # 搜索框
        condition1.connector = 'OR'
        if kew_word and self.show_search_form:
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
        # 如果不对'page'参数进行过滤，条件中就会添加'page'，查询数据库时会出错，但在其他
        # 应用场景中，可以不过滤'page'参数，分页器中会进行过滤
        for field in self.request.GET.keys():
            value_list = self.request.GET.getlist(field)
            if field != 'page':
                pager_params.setlist(field, value_list)
                if field != self.search_input_name:
                    # 搜索框的关键字要过滤掉
                    condition2.children.append(('%s__in' % field, value_list))

        final_cond = condition1 & condition2
        return pager_params, final_cond

    def changelist_view(self, request, *args, **kwargs):
        """
        展示记录
        """
        if request.method == 'GET':
            pager_params, condition = self.get_search_condition()
            obj_list = self.model_class.objects.filter(condition).order_by(
                *self.get_order_by_condition()).distinct()  # 根据条件查询数据库

            ### 实例化ChangeList对象 ###
            cl = ChangeList(self, obj_list, pager_params)  # 传入当前对象

            return render(request, 'thanos/changelist_view.html', {"cl": cl})
        else:
            # actions操作使用POST请求
            action_func = getattr(self, request.POST.get('actions'))
            ret = action_func(request)  # 派生类中需要定义对应的方法
            if ret:
                return ret  # 如果定义的方法有返回值，则使用该方法的返回值进行return

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
            add_form = model_form()
            return render(request, 'thanos/add_view.html',
                          {"config_obj": self, "add_form": add_form})
        else:
            add_form = model_form(data=request.POST)
            if not add_form.is_valid():
                return render(request, 'thanos/add_view.html',
                              {"config_obj": self, "add_form": add_form})
            else:
                new_obj = add_form.save()

                # 跳转
                _popback_id = request.GET.get('popback_id')
                if _popback_id:
                    from django.db.models.fields.reverse_related import ManyToOneRel, OneToOneRel, ManyToManyRel

                    popback_info = {"status": None, "text": None, "value": None, "popback_id": _popback_id}

                    back_related_name = request.GET.get('related_name')
                    back_model_name = request.GET.get('model_name')

                    for rel_field_obj in new_obj._meta.related_objects:
                        # 遍历所有关联当前记录所在表的其他表的字段对象，例如：teachers、headmaster
                        _related_name = str(rel_field_obj.related_name)
                        _model_name = rel_field_obj.field.model._meta.model_name

                        if _related_name == back_related_name and _model_name == back_model_name:
                            # 定位到打开popup的标签对应的字段
                            _limit_choices_to = rel_field_obj.limit_choices_to

                            if (type(rel_field_obj) == ManyToOneRel) or (type(rel_field_obj) == OneToOneRel):
                                _field_name = rel_field_obj.field_name
                            else:
                                # ManyToManyRel没有field_name方法，反应到models里面是因为没有to_field方法
                                _field_name = 'pk'

                            is_exists = self.model_class.objects.filter(pk=new_obj.pk, **_limit_choices_to).exists()
                            if is_exists:
                                # 如果新记录对象符合原limit_choices_to的条件
                                popback_info["status"] = True
                                popback_info["text"] = str(new_obj)
                                popback_info["value"] = getattr(new_obj, _field_name)

                                return render(request, 'thanos/popUp_response.html',
                                              {"popback_info": json.dumps(popback_info)})

                    return render(request, 'thanos/popUp_response.html', {"popback_info": json.dumps(popback_info)})

                else:
                    next_to = request.GET.get(self.query_dict_key)
                    if next_to:
                        return redirect('%s?%s' % (self.get_changelist_url(), next_to))
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
            change_form = model_form(instance=current_obj)
            return render(request, 'thanos/change_view.html',
                          {"self": self, "change_form": change_form})
        else:
            change_form = model_form(instance=current_obj, data=request.POST)
            if not change_form.is_valid():
                return render(request, 'thanos/change_view.html',
                              {"self": self, "change_form": change_form})
            else:
                change_form.save()

                next_to = request.GET.get(self.query_dict_key)
                if next_to:
                    return redirect('%s?%s' % (self.get_changelist_url(), next_to))
                else:
                    return redirect('%s' % self.get_changelist_url())


class CrmSite:
    '''用于分发下的基础URL，并遍历所有注册的类，获取每个类对应的表下的增删改查等URl'''

    def __init__(self):
        self._registry = {}

    def register(self, model_class, config_class=None):
        if not config_class:
            config_class = CrmConfig
        self._registry[model_class] = config_class(model_class, self)

    def get_urls(self):
        urlpatterns = []
        for model, config_obj in self._registry.items():
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            urlpatterns += [url(r'^%s/%s/' % (app_label, model_name), include(config_obj.urls, None, None))]

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), None, None


site = CrmSite()
