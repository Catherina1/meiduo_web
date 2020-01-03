from django.shortcuts import render
from django.views import View
from goods.models import GoodsCategory,GoodsChannel,GoodsChannelGroup
from .models import ContentCategory,Content


# Create your views here.
class IndexView(View):
    def get(self,request):
        # 展示首页
        # 1.展示商品分类
        categories = {}  # 整个大字典需要传给前端的数据
        channels = GoodsChannel.objects.all()  # 37个分类,group一共7个组 len(channel)=37
        # 将大致框架搭建好
        for channel in channels:
            group_id = channel.group_id  # len(group_id)=7
            # 按照小组分组，7个小组
            if group_id not in categories:
                categories[group_id] = {"channels": [], "sub_cats": []}  # 一级
            cat1 = channel.category  # channels 分类，channels外键
            # channels 列表赋值
            categories[group_id]['channels'].append({
                'id': cat1.id,
                'name': cat1.name,  # cat1 = 手机
                'url': channel.url
            })
            # 二级（cat1 的所有下级数据（Goodscategory是个自关联的表））
            for cat2 in cat1.subs.all():
                cat2.sub_cats = []
                for cat3 in cat2.subs.all():
                    cat2.sub_cats.append(cat3)
                categories[group_id]['sub_cats'].append(cat2)

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
