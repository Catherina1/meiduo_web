import os
from alipay import AliPay
from django.conf import settings
from django.shortcuts import render
# Create your views here.
from django.views import View
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from orders.models import OrderInfo
from django import http
from meiduo_mall.utils.response_code import RETCODE
from payment.models import Payment


class PaymentView(LoginRequiredJSONMixin, View):
    """订单支付"""

    def get(self, request, order_id):
        """
        :param order_id: 当前要支付的订单ID
        :return: JSON
        """
        user = request.user
        # 校验order_id
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user,
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

        # 创建对接支付宝接口的SDK对象(pip install  python-alipay-sdk==1.9 经多次使用2.0以上版本报错，脑阔疼)
        alipay = AliPay(  # 传入公共参数（对接任何接口都要传递的）
            appid=settings.ALIPAY_APPID,  # 应用ID
            app_notify_url=None,  # 默认回调url，如果采用同步通知就不传
            # 应用的私钥和支付宝公钥的路径
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",  # 加密标准
            debug=settings.ALIPAY_DEBUG  # 指定是否是开发环境
        )

        # SDK对象对接支付宝支付的接口，得到登录页的地址
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单编号
            total_amount=str(order.total_amount),  # 订单支付金额
            subject="美多商城%s" % order_id,  # 订单标题
            return_url=settings.ALIPAY_RETURN_URL  # 同步通知的回调地址，如果不是同步通知，就不传
        )

        # 拼接完整的支付宝登录页地址
        # 电脑网站支付(正式环境)，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 电脑网站支付(开发环境)，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})


class PaymentStatusView(View, LoginRequiredJSONMixin):
    """保存订单支付状态"""

    def get(self, request):
        """获取到所有的查询字符"""
        # 因为支付宝回调过来的有很多字符（文档中可以查询到）
        query_dict = request.GET
        # 将字符串转换成标准的字典类型
        data = query_dict.dict()
        # 从查询字符串参数中删除 sign , 因为这个不能参与签名验证（因为最后需要拿这个签名做比较）
        signature = data.pop('sign')

        # 使用SDK对象， 调用验证通知接口函数，得到验证结果
        # 创建支付宝支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        # 校验这个重定向是否是alipay重定向过来的,这个校验方法返回的布尔值
        success = alipay.verify(data, signature)
        if success:
            # 如果验证通过，对支付宝的支付状态进行处理
            order_id = data.get('out_trade_no')  # 读取订单号
            trade_id = data.get('trade_no')  # 读取支付宝订单流水号
            # 保存payment的订单数据
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            # 修改订单状态为待评价
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])
            # 响应trade_id
            context = {
                'trade_id': trade_id
            }
            return render(request, 'pay_success.html', context)
        else:
            # 订单支付失败，重定向到我的订单
            return http.HttpResponseForbidden('非法请求')





