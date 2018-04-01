from importlib import import_module
from CRM.settings import MESSAGE_CLASSES


def send_notification(to_name, to_addr, subject, body):
    """
    从配置中获取所有通知方式对应的类，通过反射实例化，并执行send()方法
    :param to_name: 收件人姓名
    :param to_addr: 收件人联系方式
    :param subject: 通知主题
    :param body: 通知内容
    """

    for class_path in MESSAGE_CLASSES:
        module_path, class_name = class_path.rsplit('.', 1)
        module = import_module(module_path)
        obj = getattr(module, class_name)()
        obj.send(to_name, to_addr, subject, body)
