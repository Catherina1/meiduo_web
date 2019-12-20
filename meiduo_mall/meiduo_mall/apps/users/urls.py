from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^username/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobile/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),
    url(r'^emails/$', views.EmailView.as_view(), name='email'),
    url(r'^emails/verification/$', views.EmailVerifyView.as_view(), name='email_verify'),
    url(r'^address/$', views.AddressView.as_view(), name='address'),
    url(r'^addresses/create/$', views.CreateAddressView.as_view(), name='address_create'),
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view(), name='address_update'),
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view(), name='address_default'),
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view(), name='address_title'),
]