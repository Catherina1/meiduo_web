import logging
from random import randint
from django.shortcuts import render
from django import http
from django.views import View
from django_redis import get_redis_connection
from meiduo_mall.apps.verifications.libs.captcha.captcha import captcha
from meiduo_mall.apps.verifications import constants
# Create your views here.
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.apps.verifications.libs.yuntongxun.ccp_sms import CCP


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


class SMSCodeView(View):
    def get(self,request,mobile):
        # 获取参数
        image_code_client = request.GET.get('image_code')
        uuid_client = request.GET.get('uuid')
        # 判断参数是否完整
        if not all([image_code_client, uuid_client]):
            return http.HttpResponseForbidden('缺少必要参数')
        # 连接到redis
        redis_conn = get_redis_connection('verify_code')
        # 从redis_conn中拿到图片验证码
        image_code_server = redis_conn.get('img_%s' % uuid_client)
        # 判断一下图形验证码是否存在，前面生成有设置验证码存活时间
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已失效'})
        # 删除图形验证码，如果存在则已经放入变量中，若是不存在则上面判断返回
        redis_conn.delete('img_%s' % uuid_client)
        # 前后端图形验证码比对,转码后使用小写比对
        image_code_server = image_code_server.decode()
        if image_code_server.lower() != image_code_client.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})

        # 随机生成短信验证码
        sms_code = '%06d'%randint(0, 999999)
        # 创建一个日志展示一下生成的验证码
        logger = logging.getLogger('django')
        logger.info("sms_code:%s"%sms_code)
        # 保存短信验证码
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                constants.SEND_SMS_TEMPLATE_ID)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})








