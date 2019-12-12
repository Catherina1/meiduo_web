from celery_task.main import celery_app
from django.core.mail import send_mail
from django.conf import settings


@celery_app.task(name='send_verify_email')
def send_verify_email(to_email, verify_url):
    '''
    :param to_email: 收件人
    :param verify_url: 验证链接
    :return:
    '''
    # 准备的邮件标题以及主体信息
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)

    # django包装的发送邮件的方法
    send_mail(subject, "", html_message=html_message, from_email=settings.EMAIL_FROM, recipient_list=[to_email])

