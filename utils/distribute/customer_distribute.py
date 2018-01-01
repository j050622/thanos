"""
使用Redis实现自动获取课程顾问id
"""
import redis
from app03 import models

# 连接redis
POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, password='abc123')
conn = redis.Redis(connection_pool=POOL)


class Distribute:
    """用户自动分配，从redis中获取数据"""

    @classmethod
    def get_distribution(cls):
        """获取权限分配表"""
        obj_list = models.ConsultantWeight.objects.all().order_by('-weight').values_list('consultant_id', 'cus_limit')

        if not obj_list:
            return False
        else:
            tmp_list = []

            n = 0
            while 1:
                flag = False
                for sub_lst in obj_list:
                    if sub_lst[1] > n:
                        tmp_list.append(sub_lst[0])
                        flag = True
                n += 1
                if not flag:
                    break

            conn.rpush('cons_id_list_origin', *tmp_list)
            conn.rpush('cons_id_list', *tmp_list)
            return True

    @classmethod
    def get_consultant_id(cls):
        """从redis的分配表中获取当前要被分配客户的课程顾问的id"""

        list_origin_len = conn.llen('cons_id_list_origin')
        if not list_origin_len:
            # 分配表还未生成
            status = cls.get_distribution()
            if not status:
                return None

        list_len = conn.llen('cons_id_list')
        if not list_len:
            # 分配表数据已取空
            if conn.get('reset'):
                conn.delete('cons_id_list_origin')
                status = cls.get_distribution()
                conn.delete('reset')
                if not status:
                    return None
            else:
                cnt = conn.llen('cons_id_list_origin')
                for i in range(cnt):
                    val = conn.lindex('cons_id_list_origin', i)
                    conn.rpush('cons_id_list', val)

        return conn.lpop('cons_id_list')

    @classmethod
    def reset(cls):
        conn.set('reset', True)

    @classmethod
    def rollback(cls, cid):
        conn.lpush('cons_id_list', cid)
