"""
登录之后，取出当前用户的权限，做成一定格式的数据结构，写入session
"""


def init_permission(request, user_obj):
    userinfo_obj = user_obj.userinfo
    tmp_dict = {"id": userinfo_obj.pk,
                "name": userinfo_obj.name,
                "department_id": userinfo_obj.department_id}
    request.session["userinfo"] = tmp_dict

    data_list = user_obj.roles.values('permissions__id', 'permissions__title', 'permissions__url',
                                      'permissions__code',
                                      'permissions__menu_ref_id', 'permissions__group_id',
                                      'permissions__group__menu_id', 'permissions__group__menu__title').distinct()

    # '''权限匹配'''
    # perm_info_dict = {}
    # for dict_item in data_list:
    #     group_id = dict_item.get('permissions__group_id')
    #     if group_id not in perm_info_dict:
    #         perm_info_dict[group_id] = {
    #             'urls_info': [{'url_title': dict_item.get('permissions__title'),
    #                            'url': dict_item.get('permissions__url')}],
    #             'codes': [dict_item.get('permissions__code')]
    #         }
    #     else:
    #         perm_info_dict[group_id]['urls_info'].append({'url_title': dict_item.get('permissions__title'),
    #                                                       'url': dict_item.get('permissions__url')})
    #         perm_info_dict[group_id]['codes'].append(dict_item.get('permissions__code'))
    #
    # request.session['perm_info_dict'] = perm_info_dict
    #
    # '''菜单展示'''
    # perm_side_list = []
    # for dict_item in data_list:
    #     tmp_dict = {
    #         'url_id': dict_item.get('permissions__id'),
    #         'url_title': dict_item.get('permissions__title'),
    #         'url': dict_item.get('permissions__url'),
    #         'menu_ref': dict_item.get('permissions__menu_ref_id'),
    #         'menu_id': dict_item.get('permissions__group__menu_id'),
    #         'menu_title': dict_item.get('permissions__group__menu__title')
    #     }
    #     perm_side_list.append(tmp_dict)
    # # print(perm_side_list)
    # # perm_side_list = [
    # #     {'url_id': 1, 'url_title': '用户信息', 'url': '/userinfo/', 'menu_ref': None, 'menu_id': 1, 'menu_title': '用户组'},
    # #     {'url_id': 2, 'url_title': '添加用户', 'url': '/userinfo/add/', 'menu_ref': 1, 'menu_id': 1, 'menu_title': '用户组'},
    # #     {'url_id': 3, 'url_title': '编辑用户信息', 'url': '/userinfo/edit/(\\d+)/', 'menu_ref': 1, 'menu_id': 1,'menu_title': '用户组'},
    # #     {'url_id': 4, 'url_title': '删除用户', 'url': '/userinfo/del/(\\d+)/', 'menu_ref': 1, 'menu_id': 1,'menu_title': '用户组'},
    # #     {'url_id': 5, 'url_title': '订单列表', 'url': '/order/', 'menu_ref': None, 'menu_id': 2, 'menu_title': '订单组'},
    # #     {'url_id': 6, 'url_title': '添加订单', 'url': '/order/add/', 'menu_ref': 5, 'menu_id': 2, 'menu_title': '订单组'},
    # #     {'url_id': 7, 'url_title': '编辑订单信息', 'url': '/order/edit/(\\d+)/', 'menu_ref': 5, 'menu_id': 2,'menu_title': '订单组'},
    # #     {'url_id': 8, 'url_title': '删除订单', 'url': '/order/del/(\\d+)/', 'menu_ref': 5, 'menu_id': 2,'menu_title': '订单组'},
    # #     {'url_id': 9, 'url_title': '主页', 'url': '/', 'menu_ref': None, 'menu_id': 3, 'menu_title': '其他组'},
    # #     {'url_id': 10, 'url_title': '注销', 'url': '/logout/', 'menu_ref': 9, 'menu_id': 3, 'menu_title': '其他组'}]
    #
    # request.session['perm_side_list'] = perm_side_list
