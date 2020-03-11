import os

from django.conf import settings
from django.template import loader

from .models import ContentCategory
from .utils import get_categories


def generate_static_index_html():
    """
    为了改进性能，将动态主页生成静态主页
    """
    # 1.获取商品频道和分类
    categories = get_categories()

    # 2. 获取广告内容
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 3.渲染模板
    context = {
        'categories': categories,
        'contents': contents
    }
    # 4.获取模板文件
    template = loader.get_template('index.html')
    # 5.渲染首页html页面
    html_txt= template.render(context)
    # 6.将首页html字符串写入到指定目录，命名'index.html'
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_txt)