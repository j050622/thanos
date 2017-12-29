import re

# from django.utils.deprecation import MiddlewareMixin
# from django.conf import settings
from CRM import settings
from django.shortcuts import render, redirect, reverse, HttpResponse


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
    """登录认证，权限分配"""

    def process_request(self, request):
        current_url = request.path

        # 跳过白名单URL
        for url in settings.VALID_URLS:
            re_url = "^{}$".format(url)
            if re.match(re_url, current_url):
                return None

        # 验证session
        userinfo_dict = request.session.get('userinfo')
        if not userinfo_dict:
            return redirect(reverse('login'))
