from django import http
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from meiduo_mall.utils.response_code import RETCODE
from . import models
import logging
logger = logging.getLogger('django')


# Create your views here.
class AreasView(LoginRequiredMixin, View):
    """省市级三级联动"""
    def get(self, request):
        area_id = request.GET.get('area_id')
        if not area_id:
            """省份数据没有父级id"""
            # 读取省份缓存数据
            province_list = cache.get('province_list')
            # 如果缓存没有，则写入redis
            if not province_list:
                try:
                    """查询所有省份"""
                    province_list = []
                    province_model_list = models.Area.objects.filter(parent__isnull=True)  # 查询所有父级是否为空的数据
                    for province_model in province_model_list:
                        province_list.append({'id': province_model.id, 'name': province_model.name})
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg': '省份数据哟错'})
                # 写入cache
                cache.set('province_list', province_list, 3600)
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            """查询市级或者区（两者都可以用）"""
            sub_data = cache.get('sub_data'+area_id)
            if not sub_data:
                try:
                    # get 和 filter 过滤条件的使用
                    # 属性名称__比较运算符 = 值 （filter可以使用）
                    parent_model = models.Area.objects.get(id=area_id)  # 查询市或区的父级
                    sub_model_list = parent_model.subs.all()  # 查询市的下级省,subs是根据定义外键字段时,定义的一个related_name
                    sub_list = []
                    for sub_model in sub_model_list:
                        sub_list.append({'id': sub_model.id, 'name': sub_model.name})
                    sub_data = {
                        'id': parent_model.id,  # 父级pk
                        'name': parent_model.name,  # 父级name
                        'subs': sub_list  # 父级的子集
                    }
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区数据错误'})
                # 存到cache中
                cache.set('sub_data_'+ area_id, sub_data, 3600)
            # 响应市或区数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})









