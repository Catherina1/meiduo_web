from django.conf import settings
from django.core.files.storage import Storage

from meiduo_mall.settings.dev import FDFS_BASE_URL


class FastDFSStorage(Storage):
    """
        自定义文件存储系统
        原因是因为meiduo_web_space\Lib\site-packages\django\core\files\storage.py的第142行代码
        url方法只返回了自己，即传入什么路径返回什么路径，然而我们数据库中fastdfs文件存储系统返回的图片路径是
        不全的，对数据库中的现有路径做一个拼接
        这是文档给的自定义文件存储系统的链接： https://docs.djangoproject.com/en/1.11/howto/custom-file-storage
    """
    # 文档给的优化代码提示,优化代码，简洁一点
    # def __init__(self, option=None):
    #     if not option:
    #         option = settings.CUSTOM_STORAGE_OPTIONS
    #         pass
    def __init__(self, fastdfs_url=None):
        # if not fastdfs_url:
        #     self.fastdfs_url = FDFS_BASE_URL
        # self.fastdfs_url = fastdfs_url
        self.fastdfs_url = fastdfs_url or FDFS_BASE_URL

    # 查看文档里有提到说必须写_open和_save
    def _open(self, name, mode='rb'):
        """
        用来打开文件
        :param name:打开文件的名字
        :param mode:打开文件的方式
        :return:none
        """
        pass

    def _save(self, name, content):
        """
        用于保存文件
        :param name:保存的文件名
        :param content: 文件内容对象本身
        :return: none
        """
        pass

    def url(self, name):
        """
        返回name所指文件的绝对URL
        (重写自定义url方法用于拼接传进来的name,即图片路径)
        :param name: 当前传进来的路径name:group1/M00/00/00/wKhnnlxw_gmAcoWmAAEXU5wmjPs35.jpeg
        :return: fastdfs拼接好的路径: http://192.168.103.158:8888/group1/M00/00/00/wKhnnlxw_gmAcoWmAAEXU5wmjPs35.jpeg
        """
        return self.fastdfs_url + name


