from django import http
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
from meiduo_mall.utils import views

from meiduo_mall.utils.views import LoginRequiredJSONMixin
from .utils import check_email_verify_url
from .models import User, Address
import re
from meiduo_mall.utils.response_code import RETCODE
import json
import logging
from celery_task.email.tasks import send_verify_email
from . import utils


logger = logging.getLogger('django')
# Create your views here.

# 这里使用了类视图写法，另一种方法视图实现可以实现相同效果
# def register(request):
#     # 处理GET 请求
#     if request.method == 'GET':
#         return render(request,'register.html')
#     else:
#         return HttpResponse('实现注册请求')


# 这里使用了类视图写法,一些处理都被类视图封装起来了
class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):
    """修改和删除地址"""

    def put(self, request, address_id):
        """根据传来的数据修改地址（与前端vue的创建地址同一个方法）"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 判断地址是否存在，并更新地址
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        # 构造响应的数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # 响应更新地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """删除操作"""
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将逻辑删除的值进行设定True
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})
        # 响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})



class CreateAddressView(LoginRequiredMixin, View):
    """新增用户地址"""
    def post(self, request):
        # 每个用户地址不能超过20个
        # 接收传进来的参数(注意前端传进来的参数类型)
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile, tel, email]):
            return http.HttpResponseForbidden('缺少必要的参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 新增地址成功，将新增的地址响应给前端，实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class AddressView(LoginRequiredMixin, View):
    """展示用户收货地址页面"""
    def get(self, request):
        # 获取用户地址
        login_user = request.user  # 获取当前用户
        address = Address.objects.filter(user=login_user)  # 当前用户的地址列表
        address_dict_list = []
        for address_item in address:
            address_dict = {
                "id": address_item.id,
                "title": address_item.title,
                "receiver": address_item.receiver,
                "province": address_item.province.name,
                "city": address_item.city.name,
                "district": address_item.district.name,
                "place": address_item.place,
                "mobile": address_item.mobile,
                "tel": address_item.tel,
                "email": address_item.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list,
        }

        # 返回数据到页面
        return render(request, 'user_center_site.html', context)


class EmailVerifyView(View):
    """
    邮箱链接认证
    """
    def get(self, request):

        # 1.获取链接里token的用户ID和邮箱信息(接收参数)
        token = request.GET.get('token')

        # 2.判断token是否存在或者过期
        if not token:
            return http.HttpResponseForbidden('缺少必传参数')
        #   2.1 获取token的用户信息，判断是否是当前用户
        user = check_email_verify_url(token)

        # 3.存在则email_active中保存true
        if not user:
            return http.HttpResponseForbidden('无效的token')
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮件失败')

        # 4.返回邮箱验证结果
        return redirect(reverse('users:info'))


class EmailView(views.LoginRequiredJSONMixin, View):
    """保存和绑定邮箱"""
    def put(self, request):
        # # 版本一，判断用户是否登录并返回JSON
        # if not request.user.is_authenticated():
        #     return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})

        # 1.获取邮箱数据
            # post和put方法将信息包请求体中，put方法是需要从请求体的body中拿出
            # 了解http协议的规范
            # email = request.body  # b'{"email":"723102747@qq.com"}'
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        # 2.校验邮箱数据
        if not email:
            return http.HttpResponseForbidden('缺少email参数')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        # 3.保存邮箱数据
            # 保存数据也可以使用User.objects.create,但是这个更方便
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        # 4.发送邮件
        #   4.1 生成相应的邮箱验证地址
        user = request.user
        verify_url = utils.generate_email_verify_url(user)
        to_email = email
        #   4.2 发送邮件
        send_verify_email.delay(to_email, verify_url)
        # 5.返回数据
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


# 用户中心,判断用户是否登录
class UserInfoView(LoginRequiredMixin, View):
    """使用LoginRequiredMixin可以直接判断是否登录,如果没有登录会再地址中加如next"""
    def get(self, request):
        # # 判断用户是否登录,django自定义的一个方法
        # if request.user.is_authenticated():
        #     return render(request, 'user_center_info')
        # else:
        #     return redirect(reverse('users:login'))
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }

        return render(request, 'user_center_info.html', context)


# 用户退出登录
class LogoutView(View):
    def get(self, request):
        logout(request)
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')
        return response


# 用户登录界面功能
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必要的参数哦')

        # 验证参数
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')

        # 认证数据,判断是否存在数据库里面
        # 多用户账号登录,我们再django.contrib.auth.backends 中的authenticate进行了自定义
        # 将自定义的代码放在了utils.py里,并再配置中将默认用户认证指向当前自定义的文件中
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 状态保持
        login(request, user)
        # 状态保持时间
        if remembered != 'on':
            request.session.set_expiry(0)
        else:
            # 默认None是两周后自动删除
            request.session.set_expiry(None)
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            # 返回数据
            response = redirect(reverse('contents:index'))  # 重定向转到首页
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        # return render(request, 'register.html', {'register_errmsg': '注册成功'})
        return response  # 重定向转到首页


# 用户注册功能
class Register(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        sms_code_client = request.POST.get('sms_code')

        # 判断参数是否齐全
        if not all([username,password,password2, mobile,sms_code_client, allow]): # 这个all()参数要求可迭代对象，有False就False
            return http.HttpResponseForbidden('缺少必要的参数哦')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.HttpResponseForbidden('用户格式错误')
        # 判断密码是否是8-20个字
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return http.HttpResponseForbidden('密码格式错误')
        # 判断两次密码是否一致
        if password2 != password:
            return http.HttpResponseForbidden('两次密码输入不对')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('手机号不合法')

        # 验证短信验证码
        redis_cnn = get_redis_connection('verify_code')
        sms_code_server = redis_cnn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码有误'})

        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden("请同意协议")

        try:
            # 因为使用的是django自带的用户认证系统所以不能重复
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            # 不能漏写request,报错不会提醒少了个参数，只会报哈希表的错，可以使用debug找到出错点
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        # 登入用户实现状态保持
        # Django用户认证系统提供了login()方法。
        # 封装了写入session的操作，帮助我们快速登入一个用户，并实现状态保持。
        login(request,user)
        response = redirect(reverse('contents:index'))  # 重定向转到首页
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        # return render(request, 'register.html', {'register_errmsg': '注册成功'})
        return response  # 重定向转到首页


# 使用vue的axios来发送请求,实现判断是否已注册过此用户
class UsernameCountView(View):
    def get(self, request, username):
        """
        :param request:
        :param username:
        :return:
        """
        # 使用django自带的用户认证系统给的统计功能
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


# 使用vue的axios来发送请求,实现判断是否已注册过此号码
class MobileCountView(View):
    def get(self, request, mobile):
        """
        :param request:
        :param mobile:
        :return:
        """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count':count})




