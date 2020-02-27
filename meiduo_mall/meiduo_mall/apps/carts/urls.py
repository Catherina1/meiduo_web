from django.conf.urls import url
from . import views

urlpatterns = [
    # 购物车管理
    url(r'^carts/$', views.CartsView.as_view(), name='info'),
    url(r'^carts/selection/$', views.CartSelectAllView.as_view(), name='select'),
    url(r'^carts/simple/$', views.CartSimpleView.as_view(), name='simple')
]