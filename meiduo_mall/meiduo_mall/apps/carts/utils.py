import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    """
    用户登录后把cookie的信息黑奴到redis中
    :param request: 请求的对象，通过request获取cookie中的数据
    :param user: 登陆的用户信息，可以获取user_id
    :param response: 响应对象，存进redis后将响应清楚cookie中的数据
    :return: response
    """
    # 获取cookie中的购物车数据
    cookie_cart_str = request.COOKIES.get('carts')
    # cookie中没有数据就响应结果
    if not cookie_cart_str:
        return response
    cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart_str.encode()))

    # 创建新的字典存放新的数据
    new_cart_dict = {}
    new_cart_selected_add = []
    new_cart_selected_remove = []

    # 同步cookie中购物车数据，将数据重新存放到new_cart_dict中
    for sku_id, cookie_dict in cookie_cart_dict.items():
        new_cart_dict[sku_id] = cookie_dict['count']
        # 获取cookie中购物车的选中状态
        if cookie_dict['selected']:
            new_cart_selected_add.append(sku_id)
        else:
            new_cart_selected_remove.append(sku_id)

    # 将new_cart_dict写入到Redis数据库
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    pl.hmset('carts_%s' % user.id, new_cart_dict)
    # 将勾选状态同步到Redis数据库
    if new_cart_selected_add:
        pl.sadd('selected_%s' % user.id, *new_cart_selected_add)
    if new_cart_selected_remove:
        pl.srem('selected_%s' % user.id, *new_cart_selected_remove)
    pl.execute()

    # 清除cookie
    response.delete_cookie('carts')
    return response