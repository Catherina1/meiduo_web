import logging
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from django import http
from django.views import View
from meiduo_mall.utils.response_code import RETCODE
from .models import OAuthQQUser
from .utils import generate_access_token

# Create your views here.

# 创建日志输出器
logger = logging.getLogger('django')


class QQAuthURLView(View):
    """提供qq登陆页面"""
    def get(self, request):
        # 从哪个需要登录的页面点进来,next就回到哪个页面
        next = request.GET.get('next')

        # 获取qq登陆页面网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        login_url = oauth.get_qq_url()
        print(login_url)
        # 将qq登录界面网址返回给前端js,前端js,location.href直接跳转到
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
            # 使用加密将openid放到前端界面
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
        pass







