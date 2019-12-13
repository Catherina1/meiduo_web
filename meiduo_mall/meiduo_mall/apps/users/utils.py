from django.contrib.auth.backends import ModelBackend
import re

from meiduo_mall.apps.verifications import constants
from .models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings


def generate_email_verify_url(user):
    """
    生成邮箱验证链接
    :param user: 实时用户信息
    :return: verify url
    """
    # 创建一个签名对象
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    # 使用对象对要加密的东西加密
    user_data = {'user_id': user.id, 'user_email': user.email}
    token = serializer.dumps(user_data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    return verify_url



def get_user_by_acount(username):
    """
    :param username: 用户登录传进来的用户名
    :return: 存在数据库中的用户名
    """
    try:
        if re.match(r'^1[3-9]\d{9}$', username):
            # 手机号登录
            user = User.objects.get(mobile=username)
        else:
            # 用户名登录
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    else:
        return user


class UserNameModelBackend(ModelBackend):
    # 自定义用户认证方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 获取用户登录名信息
        user = get_user_by_acount(username)
        # 检查用户和登录名是否存在
        if user and user.check_password(password):
            return user

