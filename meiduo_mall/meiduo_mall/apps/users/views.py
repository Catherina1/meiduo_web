from django.shortcuts import render
from django.views import View
# Create your views here.


class Register(View):

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        pass

