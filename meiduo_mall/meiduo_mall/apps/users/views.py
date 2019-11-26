from django import http
from django.shortcuts import render,HttpResponse
from django.views import View
import re
# Create your views here.

# 这里使用了类视图写法，另一种方法视图实现可以实现相同效果
# def register(request):
#     # 处理GET 请求
#     if request.method == 'GET':
#         return render(request,'register.html')
#     else:
#         return HttpResponse('实现注册请求')


# 这里使用了类视图写法,一些处理都被类视图封装起来了
class Register(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        # 判断参数是否齐全
        if not all([username,password,password2,mobile,allow]): # 这个all()参数要求可迭代对象，有False就False
            return http.HttpResponseForbidden('缺少必要的参数哦')
        # 判断用户名是否是5-20个字符
        if re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return http.HttpResponseForbidden('用户格式错误')
        # 判断密码是否是8-20个字
        if re.match(r'^[0-9a-zA-Z]{8,20}$',password):
            return http.HttpResponseForbidden('用户格式错误')
        # 判断两次密码是否一致
        if password2 != password:
            return http.HttpResponseForbidden('两次密码输入不对')
        # 判断手机号是否合法
        if re.match(r'^1[3-9]\d{9}$',mobile):
            return http.HttpResponseForbidden('手机号不合法')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden("请同意协议")



