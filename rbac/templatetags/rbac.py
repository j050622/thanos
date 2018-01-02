import re
import copy

from django.template import Library

register = Library()


@register.inclusion_tag('xxx.html')
def show_menu(request):
    current_url = request.path_info
    perm_side_list = request.session.get('perm_side_list')
    # print(perm_side_list)
    # perm_side_list = [
    #     {'url_id': 1, 'url_title': '用户信息', 'url': '/userinfo/', 'menu_ref': None, 'menu_id': 1, 'menu_title': '用户组'},
    #     {'url_id': 2, 'url_title': '添加用户', 'url': '/userinfo/add/', 'menu_ref': 1, 'menu_id': 1, 'menu_title': '用户组'},
    #     {'url_id': 3, 'url_title': '编辑用户信息', 'url': '/userinfo/edit/(\\d+)/', 'menu_ref': 1, 'menu_id': 1,'menu_title': '用户组'},
    #     {'url_id': 4, 'url_title': '删除用户', 'url': '/userinfo/del/(\\d+)/', 'menu_ref': 1, 'menu_id': 1,'menu_title': '用户组'},
    #     {'url_id': 5, 'url_title': '订单列表', 'url': '/order/', 'menu_ref': None, 'menu_id': 2, 'menu_title': '订单组'},
    #     {'url_id': 6, 'url_title': '添加订单', 'url': '/order/add/', 'menu_ref': 5, 'menu_id': 2, 'menu_title': '订单组'},
    #     {'url_id': 7, 'url_title': '编辑订单信息', 'url': '/order/edit/(\\d+)/', 'menu_ref': 5, 'menu_id': 2,'menu_title': '订单组'},
    #     {'url_id': 8, 'url_title': '删除订单', 'url': '/order/del/(\\d+)/', 'menu_ref': 5, 'menu_id': 2,'menu_title': '订单组'},
    #     {'url_id': 9, 'url_title': '主页', 'url': '/', 'menu_ref': None, 'menu_id': 3, 'menu_title': '其他组'},
    #     {'url_id': 10, 'url_title': '注销', 'url': '/logout/', 'menu_ref': 9, 'menu_id': 3, 'menu_title': '其他组'}]

    perm_menu_dict = {}
    for dict_item in perm_side_list:
        if not dict_item.get('menu_ref'):
            perm_menu_dict[dict_item.get('url_id')] = copy.deepcopy(dict_item)

    # print(perm_menu_dict)
    # perm_menu_dict = {
    #     1: {'url_id': 1, 'url_title': '用户信息', 'url': '/userinfo/', 'menu_ref': None, 'menu_id': 1, 'menu_title': '用户组'},
    #     5: {'url_id': 5, 'url_title': '订单列表', 'url': '/order/', 'menu_ref': None, 'menu_id': 2, 'menu_title': '订单组'},
    #     9: {'url_id': 9, 'url_title': '主页', 'url': '/', 'menu_ref': None, 'menu_id': 3, 'menu_title': '其他组'}}

    for dict_item in perm_side_list:
        url = dict_item.get('url')
        re_url = "^{}$".format(url)
        if re.match(re_url, current_url):
            menu_ref_id = dict_item.get('menu_ref')
            if not menu_ref_id:
                perm_menu_dict[dict_item.get('url_id')]['active'] = True
            else:
                perm_menu_dict[menu_ref_id]['active'] = True
    # print(perm_menu_dict)
    # perm_menu_dict = {
    #     1: {'url_id': 1, 'url_title': '用户信息', 'url': '/userinfo/', 'menu_ref': None, 'menu_id': 1, 'menu_title': '用户组',
    #         'active': True},
    #     5: {'url_id': 5, 'url_title': '订单列表', 'url': '/order/', 'menu_ref': None, 'menu_id': 2, 'menu_title': '订单组'},
    #     9: {'url_id': 9, 'url_title': '主页', 'url': '/', 'menu_ref': None, 'menu_id': 3, 'menu_title': '其他组'}}

    side_dict = {}
    for dict_item in perm_menu_dict.values():
        menu_id = dict_item.get('menu_id')
        active = dict_item.get('active')
        if not (menu_id in side_dict):
            side_dict[menu_id] = {
                'menu_title': dict_item.get('menu_title'),
                'menu_active': active,
                'urls_info': [{'url_title': dict_item.get('url_title'), 'url': dict_item.get('url'), 'active': active}]
            }
        else:
            if active:
                side_dict[menu_id]['menu_active'] = True
            side_dict[menu_id]['urls_info'].append(
                {'url_title': dict_item.get('url_title'), 'url': dict_item.get('url')})
    # print(side_dict)
    # side_dict = {1: {'menu_title': '用户组', 'menu_active': True,
    #                  'urls_info': [{'url_title': '用户信息', 'url': '/userinfo/', 'active': True}]},
    #              2: {'menu_title': '订单组', 'menu_active': None,
    #                  'urls_info': [{'url_title': '订单列表', 'url': '/order/', 'active': None}]},
    #              3: {'menu_title': '其他组', 'menu_active': None,
    #                  'urls_info': [{'url_title': '主页', 'url': '/', 'active': None}]}}

    return {"side_dict": side_dict}
