from django import http
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.views import View

from meiduo_mall.utils.response_code import RETCODE
from .utils import get_breadcrumb
from .models import GoodsCategory, SKU
from contents.utils import get_categories
# Create your views here.


class HotView(View):
    """查询列表页热销排行"""
    def get(self, request, category_id):
        # 1. 根据销量排序
        skus = SKU.objects.filter(category_id = category_id, is_launched=True).order_by('-sales')[:2]
        # 2. 封装成json数据
        hot_sku = []
        for sku in skus:
            hot_sku.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price,
            })
        json_context = {
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'hot_sku': hot_sku,
        }
        return http.JsonResponse(json_context)


class ListView(View):
    def get(self, request, category_id, page_num):
        """获取商品列表页"""
        # 1. 测试此商品类别是否存在
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('参数id不存在')
        # 2. 查询商品分类数据
        categories = get_categories()

        # 3. 查询商品面包屑导航
        breadcrumb = get_breadcrumb(category)

        # 4. 按照排序规则查询该分类商品SKU信息
        sort = request.GET.get('sort', 'default')
        # 这个排序必须拿的是模型类里定义的字段
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = 'create_time'
        # 一查多（使用【“一”的模型类对象】.【多的模型类名小写_set】.【查询方法】）
        skus = category.sku_set.filter(is_launched=True).order_by(sort_field)
        # skus = SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)

        # 5. 添加分页查询功能
        # 创建分页器
        paginator = Paginator(skus, 5)  # 分成5页
        # 获取每页商品数据
        try:
            # 获取当前页数的数据
            page_skus = paginator.page(page_num)
        except EmptyPage:
            return http.HttpResponseNotFound('empty page')
        # 获取列表总页数
        total_page = paginator.num_pages

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        return render(request, 'list.html', context)
