import re

from CRM import settings
from django.shortcuts import render, redirect, reverse, HttpResponse


# from django.utils.deprecation import MiddlewareMixin
# 为避免一些BUG，把该类复制到此处进行继承
class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


class RbacMiddleware(MiddlewareMixin):
    """
    把当前URL与当前登录用户的所有权限做匹配
    """

    def process_request(self, request):
        current_url = request.path_info

        # 跳过白名单URL
        for url in settings.VALID_URLS:
            re_url = "^{}$".format(url)
            if re.match(re_url, current_url):
                return None

        # 登录验证
        userinfo_dict = request.session.get('userinfo')
        if not userinfo_dict:
            return redirect(reverse('login'))

        # 权限匹配
        perm_info_dict = request.session.get(settings.PERM_INFO_DICT)

        flag = False
        for dict_item in perm_info_dict.values():
            for url_dict in dict_item['urls_info']:
                re_url = "^{}$".format(url_dict.get('url'))
                if re.match(re_url, current_url):
                    request.session[settings.PERM_CODES_LIST] = dict_item['codes']
                    flag = True
                    break
            if flag:
                break

        if not flag:
            return HttpResponse('无权访问')
