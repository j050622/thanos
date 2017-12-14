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
            url(r'^(\d+)/delete$', self.delete_view, name='%s_%s_delte' % info),
            url(r'^(\d+)/change$', self.change_view, name='%s_%s_change' % info),
        ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), None, None
        # return self.get_urls()

    # 增删改查对应的视图函数
    def changelist_view(self, request, *args, **kwargs):
        return HttpResponse('列表')

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
        for model, config_obj in self._registry:
            app_label = model._meta.app_lable
            model_name = model._meta.model_name
            urlpatterns += [url(r'^%s/%s/' % (app_label, model_name), include(config_obj.urls))]

            ######待整理######
            if app_label not in app_labels_list:
                app_labels_list.append(app_label)
                ######
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), None, None


site = CrmSite()
