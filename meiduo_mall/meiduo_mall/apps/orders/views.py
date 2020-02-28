from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
# Create your views here.
from django.views import View


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""
    def get(self, request):
        """提供订单结算界面"""
        return render(request, 'place_order.html')
