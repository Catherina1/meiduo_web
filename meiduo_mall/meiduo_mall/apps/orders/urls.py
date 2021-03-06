from django.conf.urls import url
from . import views

urlpatterns = [
    # 订单页面管理
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='order'),
    url(r'^orders/commit/$', views.OrderCommitView.as_view(), name='order_commit'),
    url(r'^orders/success/$', views.OrderSuccessView.as_view(), name='order_success'),
    url(r'^orders/info/(?P<page_num>\d+)/$', views.UserOrderInfoView.as_view(), name='info'),
    url(r'^orders/comment/$', views.OrderCommentView.as_view(), name='comment'),
]