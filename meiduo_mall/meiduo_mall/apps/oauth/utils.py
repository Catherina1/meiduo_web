from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings


def generate_access_token(openid):
    serializer = Serializer(settings.SECRET_KEY, expires_in=600)
    data = {'openid': openid}
    # 生成加密的token
    token = serializer.dumps(data)
    return token.decode()


def get_openid_no_pwd(openid_web):
    serializer = Serializer(settings.SECRET_KEY, expires_in=600)

    # 反序列化openid密文
    try:
        openid_web = serializer.loads(openid_web)
    except BadData:
        # 密钥过期
        return None
    else:
        return openid_web.get('openid')