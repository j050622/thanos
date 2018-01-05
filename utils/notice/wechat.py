import json
import requests


def get_access_token():
    """
    获取微信全局接口的凭证(默认有效期2个小时)
    如果每天请求次数过多, 通过设置缓存即可
    """
    result = requests.get(
        url="https://api.weixin.qq.com/cgi-bin/token",
        params={
            "grant_type": "client_credential",
            "appid": "wxc2a822a532b95810",
            "secret": "3866e3e38332a1d450b45434500bbb27",
        }
    ).json()

    if result.get("access_token"):
        access_token = result.get('access_token')
    else:
        access_token = None
    return access_token


def send_custom_msg(wechat_id, msg):
    """发送普通自定义消息"""

    access_token = get_access_token()

    body = {
        "touser": wechat_id,
        "msgtype": "text",
        "text": {
            "content": msg
        }
    }
    response = requests.post(
        url="https://api.weixin.qq.com/cgi-bin/message/custom/send",
        params={
            'access_token': access_token
        },
        data=bytes(json.dumps(body, ensure_ascii=False), encoding='utf-8')
    )
    # 这里可根据回执code进行判定是否发送成功(也可以根据code根据错误信息)
    result = response.json()
    print(result)


def send_template_msg(wechat_id, tem_name, tem_course):
    """发送模板消息"""

    access_token = get_access_token()

    response = requests.post(
        url="https://api.weixin.qq.com/cgi-bin/message/template/send",
        params={
            'access_token': access_token
        },
        json={
            "touser": wechat_id,
            "template_id": '1ZYSMEHDdht8qdtDI9Tzln38wKo7gyp88zpAPQid9v4',
            "data": {
                "first": {
                    "value": tem_name,
                    "color": "#173177"
                },
                "keyword1": {
                    "value": tem_course,
                    "color": "#173177"
                },
            }
        }
    )
    result = response.json()
    print(result)


if __name__ == '__main__':
    wechat_id = 'oAKVr1secTVhwGZj8z5cIF3h91JI'  # 微信ID应该从数据库获取
    send_custom_msg(wechat_id, '发送内容测试...')
    send_template_msg(wechat_id, 'Mark', 'Python全栈开发')
