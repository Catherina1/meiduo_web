from django.shortcuts import render
from django.views import View
from goods.models import GoodsCategory,GoodsChannel,GoodsChannelGroup
from .models import ContentCategory
from .utils import get_categories


# Create your views here.
class IndexView(View):
    def get(self,request):
        # 展示首页
        # 1.展示商品分类
        categories = get_categories(self, request)
        # 2.展示轮播图等图片商品广告
        content = {}
        # 获取广告分类（分类一共有25种）
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            # 使用一查多，使用一这方的模型类对象（cat）.点出多的一方的模型类名小写+_set 进行获取数据
            content[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': categories,
            'contents': content
        }

        return render(request, 'index.html', context)
