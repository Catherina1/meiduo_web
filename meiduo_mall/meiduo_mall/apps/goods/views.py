import datetime
from django import http
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from meiduo_mall.utils.response_code import RETCODE
from .utils import get_breadcrumb
from .models import GoodsCategory, SKU, GoodsVisitCount
from contents.utils import get_categories
# Create your views here.


# 统计分类商品访问量
class DetailVisitView(View):
    """详情分类商品统计访问量"""

    def post(self, request, category_id):
        """ajax 发来的请求，从而让统计访问次数"""
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('缺少必传参数')

        # 获取当天日期
        t = timezone.localtime()
        today_str = '%d-%02d-%02d' % (t.year, t.month, t.day)
        today_date = datetime.datetime.strptime(today_str, '%Y-%m-%d')

        try:
            # 查询今天该类别的商品访问量
            counts_data = category.goodsvisitcount_set.get(date=today_date)
        except GoodsVisitCount.DoesNotExist:
            # 如果该类别的商品在今天没有过访问记录，就新建一个访问记录
            counts_data = GoodsVisitCount()

        try:
            counts_data.category = category
            counts_data.count += 1
            counts_data.save()
        except Exception as e:
            # logger.error(e)
            return http.HttpResponseServerError('服务器异常')

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


# 商品详情页
class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """提供商品详情页"""
        # 1.接收和校验参数
        try:
            # sku = SKU.objects.filter(id=sku_id).first()  # 返回列表
            sku = SKU.objects.get(id=sku_id)  # get 方法获取的是精确数据
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 2.商品频道分类数据
        categories = get_categories()

        # 3.面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 4.热销排行
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
        }

        return render(request, 'detail.html', context)


# 热销排行
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


# 商品列表页
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
