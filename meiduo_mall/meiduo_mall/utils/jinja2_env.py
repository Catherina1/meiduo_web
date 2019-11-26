from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse


def jinja2_environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,  # 为了方便后面使用这个原生的模板方法{{ static（‘’） }},还有别忘记.url
        'url': reverse,  # 同理啊，一样是加了一个{{ url('') }}
    })
    return env
