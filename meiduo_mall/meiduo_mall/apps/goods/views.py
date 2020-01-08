from django import http
from django.shortcuts import render
from django.views import View
from .models import GoodsCategory

# Create your views here.


class ListView(View):
    def get(self, request, category_id, page_num):
        """获取商品列表页"""
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('参数id不存在')
        return render(request, 'list.html')
