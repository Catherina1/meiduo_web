from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from users.models import Address
from goods.models import SKU


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
        #{sku_id:count}
        redis_cart = redis_conn.hgetall('carts_%s'%user.id)
        #{sku_id}
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
