from django import http
from django.shortcuts import render
from django.views import View
from .utils import get_breadcrumb
from .models import GoodsCategory, SKU
from contents.utils import get_categories
# Create your views here.


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


        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
        }
        return render(request, 'list.html', context)
