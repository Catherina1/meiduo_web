import logging
import re

from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.contrib.auth import login
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django import http
from django.views import View
from django_redis import get_redis_connection
from meiduo_mall.utils.response_code import RETCODE

from users.models import User
from .models import OAuthQQUser
from .utils import generate_access_token, get_openid_no_pwd

# Create your views here.

# 创建日志输出器
logger = logging.getLogger('django')


class QQAuthURLView(View):
    """提供qq登陆页面(获取qq登录地址)"""
    def get(self, request):
        # 1.从哪个需要登录的页面点进来,next就回到哪个页面，放到地址栏的state参数中，可以
        next = request.GET.get('next')

        # 2.获取qq登陆页面网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        login_url = oauth.get_qq_url()
        # print(login_url)

        # 3.将qq登录界面网址返回给前端axios,前端js,location.href直接跳转到
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})


class QQAuthUserView(View):
    """用户扫码后登录的回调处理,上一步执行完qq那边的服务器会返回一个回调地址"""
    # http://www.meiduo.site:8000/oauth_callback?code=4A013B4A990B952D26D6AFB9022AECCA&state=%2F

    def get(self, request):

        # 1.提取code
        code = request.GET.get('code')
        if code is None:
            return http.HttpResponseForbidden('回调地址缺少code')

        # 2.获取openid
        # 创建工具对象来获取access_token 和 openid
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        try:
            # 使用code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)

            # 使用access_token向QQ服务器请求openid
            open_id = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')

        # 3.通过openid判断是否绑定用户
        try:
            # 通过openid获取相对应的用户
            oauth_user = OAuthQQUser.objects.get(openid=open_id)
        except OAuthQQUser.DoesNotExist:
            # 3.1 没有找到相应openid的相关用户,则返回注册页面注册新用户
            # 使用加密将openid放到前端界面，再generate_access_token方法中已经设置存活时间
            access_token_openid = generate_access_token(open_id)
            context = {'access_token_openid': access_token_openid}
            # 返回回调注册页面
            return render(request, 'oauth_callback.html', context)

        else:
            # 3.2 如果qq用户已经绑定过openid,回主页
            qq_user = oauth_user.user
            # 状态保持
            login(request, qq_user)
            # 重定向
            # 从哪来走哪去
            state = request.GET.get('state')
            response = redirect(state)
            # 设置cookie
            response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 15)
            return response

    def post(self, request):
        """绑定用户openid信息"""

        # 1.提取表单提交的数据信息
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        # image_code = request.POST.get('image_code')
        sms_code = request.POST.get('sms_code')
        access_token_openid = request.POST.get('access_token_openid')

        # 2.简单校验数据
        if not all([mobile,password,sms_code,access_token_openid]):
            return http.HttpResponseForbidden('缺少比传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        # 3.从redis中拿到短信数据（发送短信功能再verification中）
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 判断redis中短信验证码是否存在
        if sms_code_server is None:
            return render(request,'oauth_callback.html',{'sms_code_errmsg':'验证码失效'})
        # 数据对比
        if sms_code != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg':'短信验证码错误'})

        # 4.判断openid是否有效
        # 生成反序列化密文
        openid = get_openid_no_pwd(access_token_openid)
        # 判断是否密文过期
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg':'code过期'})

        # 5.保存注册数据
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 6.用户不存在，新建一个用户
            user = User.objects.create_user(username=mobile,password=password,mobile=mobile)
        else:
            # 7.用户存在，检查密码对不对
            if not user.check_password(password):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})

        # 8.绑定openid
        try:
            OAuthQQUser.objects.create(openid=openid, user=user)
        except DatabaseError:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})

        # 9.实现状态保持
        login(request, user)

        # 10. 响应绑定结果
        next = request.GET.get('state')
        response = redirect(next)

        # 11.登录用户名写入到cookie,有效期15 天
        response.set_cookie('username',user.username, max_age=3600 * 24 * 15)
        return response



















