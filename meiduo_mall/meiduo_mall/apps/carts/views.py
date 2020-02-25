import base64
import json
import pickle

from django import http
from django.shortcuts import render
from django.views import View
# Create your views here.
from django_redis import get_redis_connection

from goods import models
from meiduo_mall.utils.response_code import RETCODE


class CartsView(View):
    """管理购物车"""

    def post(self, request):
        """添加到购物车"""

        # 1.接收校验参数
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 校验参数
        if not all([sku_id,count]):
            return http.HttpResponseForbidden('缺少必要的参数')
        # 检查sku是否存在
        try:
            models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return http.HttpResponseForbidden('没有这个商品')
        # 检查count是否为整数
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('count错误')
        # 判断selected是否为布尔值
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('selected 错误')

        # 2.判断用户是否登录，进行数据存储
        user = request.user
        if user.is_authenticated:
            # 3.用户已登录，操作redis数据库
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 新增购物车数据（使用redis中的哈希表hash数据结构）
            pl.hincrby('carts_%s' % user.id, sku_id, count)
            # 新增选中状态(只存储状态使用redis中的set数据结构存储)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            # 执行管道
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
        else:
            # 4.用户未登录, 操作cookie购物车
            cart_str = request.COOKIES.get('carts')  # 获取浏览器中的cookie
            if cart_str:  # 如果用户操作过购物车
                # 使用pickle签名模块对已经加密过的购物车数据进行反序列化
                cart_dict = pickle.loads(base64.decode(cart_str.encode()))
            else:  # 如果没有操作购物车数据，创建一个
                cart_dict = {}

            # 4.1判断该商品是否存在在购物车中，如已存在，累加求和，
            if sku_id in cart_dict:
                # 累加
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 4.2 将字典转化成可以存储的
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 4.3 创建响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
            response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response








