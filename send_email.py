# coding=utf-8
# 作者      : WU
# 创建时间   : 2019/6/14
# 文件名    : sendemail
# IDE      : PyCharm
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


class Mail:
	
	def __init__(self):
		self.name = 'Ds'
		self.sender = 'ds@checar.cn'
		self.sender_pwd = 'Ds2233'
		self.users = {
			"Ds": "ds@checar.cn",
			# "魏杰斌": "kitbun@checar.cn",
		}
	
	def mail(self, info):
		
		ret = True
		try:
			
			for x in self.users.items():
				msg = MIMEText(info, 'plain', 'utf-8')
				msg['From'] = formataddr([self.name, self.sender])
				msg['To'] = formataddr(x)
				msg['Subject'] = "服务异常邮件"
			
			server = smtplib.SMTP_SSL("smtp.exmail.qq.com")
			server.login(self.sender, self.sender_pwd)
			server.sendmail(self.sender, self.users.values(), msg.as_string())
			server.quit()
		except Exception as e:
			print(e)
			ret = False
		return ret


if __name__ == '__main__':
	
	t = Mail()
	info = "测试"
	ret = t.mail(info)
	if ret:
		print("邮件发送成功！")
	else:
		print("邮件发送失败！")
