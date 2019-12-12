# 异步方案，为了解耦，保证主程序不被阻塞
# celery的启动文件
from celery import Celery

# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 创建一个celery实例(生产者)
celery_app = Celery('meiduo')

# 加载celery配置,就是指定broker消息队列放在那个地方
celery_app.config_from_object('celery_task.config')

# 自动注册celery任务
celery_app.autodiscover_tasks(['celery_task.sms', 'celery_task.email'])
