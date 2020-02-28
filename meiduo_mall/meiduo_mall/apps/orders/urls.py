from django.conf.urls import url
from . import views

urlpatterns = [
    # 订单页面管理
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='order'),
]