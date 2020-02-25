from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.CartsView.as_view(), name='carts'),
]