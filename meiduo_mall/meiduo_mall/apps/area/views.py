from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
class AddressView(View):
    """用户收货地址"""
    def get(self, request):
        return render(request, 'user_center_site.html')
