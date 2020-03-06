from django.conf.urls import url
from . import views

urlpatterns = [
    # 订单页面管理
    url(r'payment/(?P<order_id>\d+)/$', views.PaymentView.as_view()),
    # url(r'^payment/(?P<order_id>\d+)/$', views.PaymentView.as_view(), name='payment_info'),
]