from django.shortcuts import render
from django.views import View
from goods.models import GoodsCategory,GoodsChannel,GoodsChannelGroup


# Create your views here.
class IndexView(View):
    def get(self,request):
        # 展示首页
        # 展示商品分类
        # {
        #     "1"(group): {
        #         "channels": [
        #             {"id": 1, "name": "手机", "url": "http://shouji.jd.com/"},
        #             {"id": 2, "name": "相机", "url": "http://www.itcast.cn/"}
        #         ],
        #         "sub_cats": [
        #             {
        #                 "id": 38,
        #                 "name": "手机通讯",
        #                 "sub_cats": [
        #                     {"id": 115, "name": "手机"},
        #                     {"id": 116, "name": "游戏手机"}
        #                 ]
        #             },
        #             {
        #                 "id": 39,
        #                 "name": "手机配件",
        #                 "sub_cats": [
        #                     {"id": 119, "name": "手机壳"},
        #                     {"id": 120, "name": "贴膜"}
        #                 ]
        #             }
        #         ]
        #     },
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
            context = {
                'categories': categories,
            }

        return render(request, 'index.html', context)
