from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.shortcuts import render
from django import http
from django.views import View
from meiduo_mall.utils.response_code import RETCODE

# Create your views here.


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