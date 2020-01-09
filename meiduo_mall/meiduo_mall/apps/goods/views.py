from django import http
from django.shortcuts import render
from django.views import View
from .utils import get_breadcrumb
from .models import GoodsCategory
from contents.utils import get_categories
# Create your views here.


class ListView(View):
    def get(self, request, category_id, page_num):
        """获取商品列表页"""
        # 测试此商品类别是否存在
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('参数id不存在')
        # 查询商品分类数据
        categories = get_categories()

        # 查询商品面包屑导航
        breadcrumb = get_breadcrumb(category)

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
        }
        return render(request, 'list.html', context)
