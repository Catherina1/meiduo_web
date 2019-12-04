from celery_task.main import celery_app
from .yuntongxun.ccp_sms import CCP


# bind：保证task对象会作为第一个参数自动传入
# name：异步任务别名
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限


@celery_app.task(name='ccp_send_sms_code')
def ccp_send_sms_code(mobile, sms_code):
    """
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: 0 or 1
    """
    try:
        send_ret = CCP().send_template_sms('18559762376', ['123456', 5], 1)
    except Exception as e:
        raise e
    print(send_ret)
    if send_ret != 0:
        print('失败')

    return send_ret
