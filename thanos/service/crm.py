from django.conf.urls import url, include
from django.shortcuts import render, redirect, reverse, HttpResponse


class CrmConfig:
    """对传入的Model表名，分配‘增删改查’等的URL"""

    # 基本配置
    list_display = []

    ######
    def __init__(self, model_class, site_obj):
        self.model_class = model_class
        self.site_obj = site_obj

    def get_urls(self):
        info = self.model_class._meta.app_label, self.model_class._meta.model_name

        urlpatterns = [
            url(r'^$', self.changelist_view, name='%s_%s_changelist' % info),
            url(r'^add/$', self.add_view, name='%s_%s_add' % info),
            url(r'^(\d+)/delete$', self.delete_view, name='%s_%s_delete' % info),
            url(r'^(\d+)/change$', self.change_view, name='%s_%s_change' % info),
        ]
        return urlpatterns

    @property
    def urls(self):
        # return self.get_urls(), None, None
        return self.get_urls() # 测试一下只返回列表会不会报错

    # 增删改查对应的视图函数
    def changelist_view(self, request, *args, **kwargs):
        # 表头

        def outer_head():
            if not self.list_display:
                yield '记录'
            for field_name in self.list_display:
                if isinstance(field_name, str):
                    verbose_name = self.model_class._meta.get_field(field_name).verbose_name
                else:
                    verbose_name = field_name(self, is_header=True)
                yield verbose_name

        # 表格主体
        obj_list = self.model_class.objects.all()

        def outer_data():
            for obj in obj_list:
                if not self.list_display:
                    yield [obj]

                def inner(obj):
                    for field_name in self.list_display:
                        if isinstance(field_name, str):
                            val = getattr(obj, field_name)
                        else:
                            val = field_name(self, obj)
                        yield val

                yield inner(obj)

        return render(request, 'thanos/changelist.html', {"head_list": outer_head(), "data_list": outer_data()})

    def add_view(self, request, *args, **kwargs):
        return HttpResponse('添加')

    def delete_view(self, request, nid, *args, **kwargs):
        return HttpResponse('删除' + nid)

    def change_view(self, request, nid, *args, **kwargs):
        return HttpResponse('修改' + nid)


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
            urlpatterns += [url(r'^%s/%s/' % (app_label, model_name), include(config_obj.urls))]
            # urlpatterns += [url(r'^%s/%s/' % (app_label, model_name), (config_obj.urls), None, None)]

            ######待整理######
            if app_label not in app_labels_list:
                app_labels_list.append(app_label)
                ######

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), None, None


site = CrmSite()
