from django import http
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
from .models import User
import re
from meiduo_mall.utils.response_code import RETCODE
from django.contrib.auth.decorators import login_required
# Create your views here.

# 这里使用了类视图写法，另一种方法视图实现可以实现相同效果
# def register(request):
#     # 处理GET 请求
#     if request.method == 'GET':
#         return render(request,'register.html')
#     else:
#         return HttpResponse('实现注册请求')


# 这里使用了类视图写法,一些处理都被类视图封装起来了
# 用户中心,判断用户是否登录
class UserInfoView(LoginRequiredMixin, View):
    """使用LoginRequiredMixin可以直接判断是否登录,如果没有登录会再地址中加如next"""
    def get(self, request):
        # # 判断用户是否登录,django自定义的一个方法
        # if request.user.is_authenticated():
        #     return render(request, 'user_center_info')
        # else:
        #     return redirect(reverse('users:login'))
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }

        return render(request, 'user_center_info.html', context)


# 用户退出登录
class LogoutView(View):
    def get(self, request):
        logout(request)
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')
        return response


# 用户登录界面功能
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必要的参数哦')

        # 验证参数
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')

        # 认证数据,判断是否存在数据库里面
        # 多用户账号登录,我们再django.contrib.auth.backends 中的authenticate进行了自定义
        # 将自定义的代码放在了utils.py里,并再配置中将默认用户认证指向当前自定义的文件中
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 状态保持
        login(request, user)
        # 状态保持时间
        if remembered != 'on':
            request.session.set_expiry(0)
        else:
            # 默认None是两周后自动删除
            request.session.set_expiry(None)
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            # 返回数据
            response = redirect(reverse('contents:index'))  # 重定向转到首页
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        # return render(request, 'register.html', {'register_errmsg': '注册成功'})
        return response  # 重定向转到首页


# 用户注册功能
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
        sms_code_client = request.POST.get('sms_code')

        # 判断参数是否齐全
        if not all([username,password,password2, mobile,sms_code_client, allow]): # 这个all()参数要求可迭代对象，有False就False
            return http.HttpResponseForbidden('缺少必要的参数哦')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.HttpResponseForbidden('用户格式错误')
        # 判断密码是否是8-20个字
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return http.HttpResponseForbidden('密码格式错误')
        # 判断两次密码是否一致
        if password2 != password:
            return http.HttpResponseForbidden('两次密码输入不对')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('手机号不合法')

        # 验证短信验证码
        redis_cnn = get_redis_connection('verify_code')
        sms_code_server = redis_cnn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码有误'})

        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden("请同意协议")

        try:
            # 因为使用的是django自带的用户认证系统所以不能重复
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            # 不能漏写request,报错不会提醒少了个参数，只会报哈希表的错，可以使用debug找到出错点
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        # 登入用户实现状态保持
        # Django用户认证系统提供了login()方法。
        # 封装了写入session的操作，帮助我们快速登入一个用户，并实现状态保持。
        login(request,user)
        response = redirect(reverse('contents:index'))  # 重定向转到首页
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        # return render(request, 'register.html', {'register_errmsg': '注册成功'})
        return response  # 重定向转到首页


# 使用vue的axios来发送请求,实现判断是否已注册过此用户
class UsernameCountView(View):
    def get(self, request, username):
        """
        :param request:
        :param username:
        :return:
        """
        # 使用django自带的用户认证系统给的统计功能
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


# 使用vue的axios来发送请求,实现判断是否已注册过此号码
class MobileCountView(View):
    def get(self, request, mobile):
        """
        :param request:
        :param mobile:
        :return:
        """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count':count})




