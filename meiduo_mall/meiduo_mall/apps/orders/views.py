import json
from decimal import Decimal
from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render
# Create your views here.
from django.utils import timezone
from django.views import View
from django_redis import get_redis_connection

from users.models import Address
from goods.models import SKU

from meiduo_mall.utils.views import LoginRequiredJSONMixin
from orders.models import OrderInfo,OrderGoods

from meiduo_mall.utils.response_code import RETCODE


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""
    def get(self, request):
        """提供订单结算界面"""
        # 获取登录用户
        user = request.user
        # 获取查询地址信息
        try:
            addresses = Address.objects.filter(user=request.user, is_deleted=False)
        except Address.DoesNotExist:
            # 如果地址为空，渲染模板时会判断，并跳转到地址编辑页面
            addresses = None

        # 查询redis中的sku_id 以及数据库中sku 信息
        redis_conn = get_redis_connection('carts')
        # {sku_id:count}
        redis_cart = redis_conn.hgetall('carts_%s'%user.id)
        # {sku_id}
        cart_selected = redis_conn.smembers('selected_%s' % user.id)
        # 新创建一个字典保存数据(被选中的字典)
        # {sku_id:count}
        new_cart_dict = {}
        for sku_id in cart_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

        # 查询sku信息
        skus_id = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=skus_id)

        total_count = 0
        total_amount = 0

        for sku in skus:
            # 动态语言可以直接给对象添加属性
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.count * sku.price
            total_count += sku.count
            total_amount += Decimal(sku.amount)
        # 运费
        freight = Decimal('10.00')
        # 渲染界面
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }
        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequiredJSONMixin, View):
    """提交订单"""

    def post(self, request):
        """保存订单信息和订单商品信息"""

        # 1.获取当前要保存的订单数据
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 2.校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)  # 不用filter是因为这个会有缓存
        except Exception:
            return http.HttpResponseForbidden('参数address_id错误')
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')

        with transaction.atomic():
            # 创建事务保存点
            save_id = transaction.savepoint()
            # 暴力回滚
            try:
                # 3.获取登录用户
                user = request.user
                # 4.生成订单编号：年月日时分秒+用户编号
                order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
                # 5.保存订单基本信息 OrderInfo（一）
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )

                # 从redis读取购物车中被勾选的商品信息
                redis_conn = get_redis_connection('carts')
                redis_cart = redis_conn.hgetall('carts_%s' % user.id)
                selected = redis_conn.smembers('selected_%s' % user.id)
                carts = {}
                for sku_id in selected:
                    carts[int(sku_id)] = int(redis_cart[sku_id])
                sku_ids = carts.keys()

                # 遍历购物车中被勾选的商品信息
                for sku_id in sku_ids:
                    # 使用循环是为了让用户提交订单冲突时还有库存的状态下再多次请求下订单
                    # 直到库存不够则跳出
                    while True:
                        # 查询SKU信息
                        sku = SKU.objects.get(id=sku_id)

                        # 获取最初的库存和销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # 判断SKU库存
                        sku_count = carts[sku.id]
                        if sku_count > sku.stock:
                            # 出错就回滚
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        # # sku减少库存
                        # sku.stock -= sku_count
                        # # sku增加销售量
                        # sku.sales += sku_count
                        # sku.save()

                        # 使用乐观锁实现多个订单并发处理,更新库存和销量
                        # 乐观锁就是数据进行前后比较有变化则不执行，无变化则执行
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        # 如果不是原始数据，不一样，则返回0
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        # 如果下单失败，但是库存足够时，继续下单，直到下单成功或者库存不足为止
                        # result 返回值0和1, 0代表数据已经有改动，则继续执行
                        if result == 0:  # 如果已经改动则不执行下方代码，跳到循环最前重新执行
                            continue

                        # spu增加
                        # (当某一型号手机卖出，那么这一大类数量也会增加)
                        sku.spu.sales += sku_count
                        sku.spu.save()

                        # 保存订单商品信息 OrderGoods（多）
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )

                        # 保存商品订单总价和数量
                        order.total_count += sku_count
                        order.total_amount += (sku_count * sku.price)
                        # 下单成功或者失败就跳出循环
                        break

                # 添加邮费和保存订单信息
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})
            # 提交订单成功，显式的提交一次事务
            transaction.savepoint_commit(save_id)
        # 响应提交订单结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})


class OrderSuccessView(LoginRequiredMixin, View):
    """订单提交成功页面"""
    def get(self, request):
        """提交订单成功页面"""
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id':order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method,
        }

        return render(request, 'order_success.html', context)




