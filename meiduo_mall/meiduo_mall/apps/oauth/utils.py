from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings


def generate_access_token(openid):
    serializer = Serializer(settings.SECRET_KEY, expires_in=600)
    data = {'openid': openid}
    # 生成加密的token
    token = serializer.dumps(data)
    return token.decode()