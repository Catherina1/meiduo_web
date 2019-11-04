from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse


def jinja2_enviroment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage,  # 为了方便后面使用这个原生的模板方法{{ static（‘’） }}
        'url': reverse(),  # 同理啊，一样是加了一个{{ url('') }}
    })
