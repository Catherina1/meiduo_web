from django.shortcuts import render
from django import http
from django.views import View
from django_redis import get_redis_connection
from meiduo_mall.apps.verifications.libs.captcha.captcha import captcha
from meiduo_mall.apps.verifications import constants
# Create your views here.


class ImageCodeView(View):
    def get(self,request,uuid):
        """
        :param request: request image
        :param uuid: image verify code
        :return: image/code
        """
        # 生成验证码和图片
        text, image = captcha.generate_captcha()

        # 保存图片和验证码
        redis_conn = get_redis_connection('verify_code')
        # 写入到redis中，第二个参数存入的是图形信息过期时间（不需要存图片）
        redis_conn.setex('img_%s'%uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return http.HttpResponse(image, content_type='image/jpg')