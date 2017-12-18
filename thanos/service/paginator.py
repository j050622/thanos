import math


class Paginator:
    def __init__(self, params_dict, obj_list, page_num, base_url, show_obj_cnt, show_ele_count=11):
        self.params_dict = params_dict
        self.obj_list = obj_list
        self.page_num = page_num
        self.base_url = base_url
        self.show_obj_cnt = show_obj_cnt
        self.show_ele_cnt = show_ele_count

    def show_obj_list(self):
        """当前页面要展示的记录列表"""

        start = (self.page_num - 1) * self.show_obj_cnt
        end = self.page_num * self.show_obj_cnt

        return self.obj_list[start:end]

    def pager_html(self):
        """生成页码按钮的html代码"""

        max_page_num = int(math.ceil(len(self.obj_list) / self.show_obj_cnt))
        params = self.params_dict.urlencode()

        ele_list = []
        # 首页
        if self.page_num == 1:
            first_page = '<li><span>首页</span></li>'
        else:
            first_page = '<li><a href="%s?page=1&%s">首页</a></li>' % (self.base_url, params)
        ele_list.append(first_page)

        # 上一页
        if self.page_num != 1:
            previous_page = '<li><a href="%s?page=%s&%s">上一页</a></li>' % (self.base_url, self.page_num - 1, params)
            ele_list.append(previous_page)

        # 普通页面标签
        if max_page_num <= self.show_ele_cnt:
            start_page = 1
            end_page = max_page_num
        else:
            half_ele_cnt = int((self.show_ele_cnt - 1) / 2)
            if self.page_num <= half_ele_cnt:
                start_page = 1
                end_page = self.show_ele_cnt
            elif self.page_num > max_page_num - half_ele_cnt:
                end_page = max_page_num
                start_page = max_page_num - half_ele_cnt * 2
                print(start_page)
            else:
                start_page = self.page_num - half_ele_cnt
                end_page = self.page_num + half_ele_cnt

        for i in range(start_page, end_page + 1):
            if i == self.page_num:
                ele_li = '<li class="active"><span>%s</span></li>' % i
            else:
                ele_li = '<li><a href="%s?page=%s&%s">%s</a></li>' % (self.base_url, i, params, i)
            ele_list.append(ele_li)

        # 下一页
        if self.page_num != max_page_num:
            next_page = '<li><a href="%s?page=%s&%s">下一页</a></li>' % (self.base_url, self.page_num + 1, params)
            ele_list.append(next_page)

        # 尾页
        if self.page_num == max_page_num:
            last_page = '<li><span>尾页</span></li>'
        else:
            last_page = '<li><a href="%s?page=%s&%s">尾页</a></li>' % (self.base_url, max_page_num, params)
        ele_list.append(last_page)

        return '\n'.join(ele_list)
