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

from meiduo_mall.apps.users import constants


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

    def get(self, request):
        """展示购物车"""
        # 1.查询用户登陆状态
        user = request.user

        if user.is_authenticated:
            # 2.如果用户登录，从redis中拿取数据
            redis_conn = get_redis_connection('carts')
            # 2.1 获取redis购物车中的数据
            redis_carts = redis_conn.hgetall('carts_%s' % user.id)
            # 2.2 获取redis中的选中状态
            cart_select = redis_conn.smembers('selected_%s' % user.id)

            # 2.3 将数据转换成和cookie中一样的格式，方便统一
            carts_dict = {}
            for sku_id, count in redis_carts.items():
                carts_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_select
                }

        else:
            # 3.用户未登录，从cookie中拿数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将字符串各种转换
                carts_dict = pickle.loads(base64.b64decode(cart_str.encode))
            else:
                carts_dict = {}

        # 4.构造展示购物车页面的数据
        sku_ids = carts_dict.keys()
        # 这种方式获取每一个sku的信息，可以使用另一种方法__in
        # for sku_id in sku_ids:
        #     skus = models.SKU.get(id = sku_id)
        # 一次性查询出所有的skus
        skus = models.SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': carts_dict.get(sku.id).get('count'),
                'selected': str(carts_dict.get(sku.id).get('selected')),
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),
                'amount': str(sku.price * carts_dict.get(sku.id).get('count'))
            })

        context = {
            'cart_skus': cart_skus,
        }

        # 5.渲染购物车页面
        return render(request, 'cart.html', context)

    def put(self, request):
        """更改购物车信息"""
        # 1. 接收校验参数
        # axios发送的请求
        # axios.put(url, {
        #     sku_id: this.carts[index].id,
        #     count: count,
        #     selected: this.carts[index].selected
        # }
        # 所以datas接收到的数据则是以上的类型
        datas = request.body.decode()
        json_dict = json.loads(datas)
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected')

        if not all([sku_id,count]):
            return http.HttpResponseForbidden('缺少必要参数')
        try:
            sku = models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品sku_id不存在')

        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('count参数错误')

        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有错')

        # 2.判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 2.1 如果用户登录，使用前端传过来最新的数据保存到redis中
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 因为是根据单一sku商品所以一次性覆盖
            pl.hset('carts_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()
            # 2.2 保存后还是需要响应
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'修改购物车成功', 'cart_sku':cart_sku})
        else:
            # 3.1 如果用户未登录，修改cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                art_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            # 覆盖掉原来的数据
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # 创建响应对象
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response











