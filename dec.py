# coding=utf-8
# 作者      : WU
# 创建时间   : 2019/6/10
# 文件名    : dec
# IDE      : PyCharm
from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
from tools.send_email import Mail
import json


def pay_dec(func):
	def inner(request):
		
		# meta = request.META
		# print(meta)
		if request.method == "GET":
			# info = request.GET.dict()
			# print(info)
			return render(request, 'up.html')
		elif request.method == "POST":
			info = request.POST.dict()
			print(info)
			# rs = {
			# 	"code": 200,
			# 	"msg": "测试",
			# 	# "result": "http:127.0.0.1:8000/" + "pay_img/?jdsbh=1311231800345254"
			# 	"result": "img/?jdsbh=1311231800345254"
			# }
			p = GH_Pay()
			# p = GH_Pay()
			
			try:
				# 创建微信工商支付对象并初始化
				rs = p.run(info)
				# rs = p.pay(info)
				m = Mail()
				m.mail(json.dumps(rs))
				return JsonResponse(rs)
			except Exception as e:
				m = Mail()
				m.mail(e)
				result = {
					"code": 404,
					"msg": e,
					"result": "/pay/img/?jdsbh=0"
				}
				p.stop()
				return JsonResponse(result)
	
	return inner
