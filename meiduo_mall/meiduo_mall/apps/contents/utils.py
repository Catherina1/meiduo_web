from collections import OrderedDict
from .models import  ContentCategory
from goods.models import GoodsCategory,GoodsChannel,GoodsChannelGroup


def get_categories():
    """获取商品的分类"""
    # 1.展示商品分类
    # categories = {}  # 整个大字典需要传给前端的数据
    categories = OrderedDict()  # 商品分类对应的字典（s使用这种字典可以是有序的字典）
    # 37个一级类别（所有商品频道）len(channel)=37
    channels = GoodsChannel.objects.all()
    # 将大致框架搭建好，遍历所有频道
    for channel in channels:
        # 获取当前频道所在的组,len(group_id)=11
        group_id = channel.group_id
        # 构造基本一级数据框架：只有11个组
        if group_id not in categories:
            categories[group_id] = {"channels": [], "sub_cats": []}  # 一级
        # 查询当前拼频道对应的一级分类
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
    return categories
