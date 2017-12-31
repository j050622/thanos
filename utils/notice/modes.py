import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


class BaseMode:
    """接口类"""

    def send(self, to_name, to_addr, subject, body):
        raise NotImplementedError("'%s' object has no attribute 'send'" % (self.__class__.__name__))


class SendEmail(BaseMode):
    """发送邮件"""

    def __init__(self):
        self.username = 'XI'
        self.addressor = '412003074@qq.com'
        self.password = 'iyjtqfuxhqgqbhba'

    def send(self, to_name, to_addr, subject, body):
        msg = MIMEText(body)
        msg['Form'] = formataddr([self.username, self.addressor])  # 发件人
        msg['To'] = formataddr([to_name, to_addr])  # 收件人
        msg['Subject'] = subject

        server = smtplib.SMTP_SSL('smtp.qq.com')
        server.login(self.addressor, self.password)  # QQ邮箱不用密码，需要授权码
        server.sendmail(self.addressor, [to_addr, ], msg.as_string())  # 发件人和收件人
        server.quit()


class SendMessage(BaseMode):
    """发送短信"""

    def __init__(self):
        self.username = 'XI'
        self.tel_number = 15500006666

    def send(self, to_name, to_addr, subject, body):
        print('模拟短信发送')


class SendWeChat(BaseMode):
    """微信公众号推送消息"""

    def __init__(self):
        self.xxx = '公众号'

    def send(self, to_name, to_addr, subject, body):
        print('模拟微信发送')
