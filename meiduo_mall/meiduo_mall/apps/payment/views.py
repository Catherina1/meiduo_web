from django.shortcuts import render
# Create your views here.
from django.views import View
from meiduo_mall.utils.views import LoginRequiredJSONMixin


class PaymentView(LoginRequiredJSONMixin, View):
    """订单支付"""
    def get(self, request, order_id):
        print(order_id)
        pass

