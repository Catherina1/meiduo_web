# meiduo_web

#### 介绍
练手商城项目一（前后端不分离）：
使用到的语言和框架有：
    django 实现
    jinja2 模板语言
    celery 异步
    elastic search 查询语言
    vue.js
    html
    css
存储：
    mysql
    redis
    容器化方案Docker
    文件存储方案FastDFS
登录付款验证：
    captcha 扩展包(用户注册图片验证码)
    容联云通讯短信平台 （短信验证）
    网站对接QQ登录
    支付宝alipay对接


#### 软件架构
软件架构说明
前后端不分离，模板渲染类型网站搭建
前端页面看到的效果都是由后端控制，由后端渲染页面或重定向，也就是后端需要控制前端的展示，前端与后端的耦合度很高。

#### 安装教程
笔记：
1.  创建一个虚拟环境，当安装了python2 和 3 两个版本，在使用【mkvirtualenv -p python3 虚拟环境名称 】这条命令不起作用，建议可以直接指向本地的python版本
【mkvirtualenv -p 解释器路径 虚拟环境名称 】
2.  需安装redis, mysql , 下载所需要的python扩展包
3.  django框架
4.  docker里要有fastdfs , elastsearch
5.  本项目是基于win开发，docker安装在Ubuntu系统的vmware虚拟机中,也可以运行在纯linux环境中，稍作修改即可
6.  相对于win, linux系统进行开发更便捷，支持的扩展包也多


#### 使用说明

1.  开发过强烈建议只使用谷歌浏览器
2.  只是一个前后端不分离的应用，后面还需要再设计一个前后端分离的后台操作管理系统，方便数据管理

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 码云特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  码云官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解码云上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是码云最有价值开源项目，是码云综合评定出的优秀开源项目
5.  码云官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  码云封面人物是一档用来展示码云会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
