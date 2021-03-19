# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from datetime import datetime
from datetime import timedelta

import shortuuid
from flask import current_app
from flask import session, render_template, request

from utils.tools import get_user_ip, get_user_referrer, IP2Region
from .views import bp

ip2region = IP2Region()


@bp.before_request
def before_request():
    from utils import zlcache
    ip = get_user_ip(request)  # 自定义封装获取ip，可以与nginx搭配使用
    if zlcache.ipget(ip):
        return render_template('front/front_404.html'), 404
    if current_app.config.get('maintenance'):  # 维护网站
        return render_template('common/maintenance.html')
    if current_app.config['VISITOR'] in session:
        pass
    # 判断后台是否开启了维护时段。
    else:
        # 如果设置session.permanent = True，那么过期时间为31天
        session.permanent = True
        current_app.permanent_session_lifetime = timedelta(days=180)
        session[current_app.config['VISITOR']] = shortuuid.uuid()  # 保存用户登录信息


@bp.after_request
def after_request(respones):
    '''
    记录登陆后的操作日志，可以将不想监控的操作加入到unpath中，监控路由对应的操作在config.py的xxx中进行添加或配置相应的说明
    例如，不想监控/xxx/ 路由
    对/xxx/l路由进行监控，并对其添加操作说明，‘审核ID:123事件为:误报’
    :param respones:
    :return:
    '''
    path = request.path
    ignore_path = ['/get_img/', '/cpu/', '/memory/', '/netio/', '/process/', '/delprocess/', '/disk/']  # 不想被写进日志忽略的路由
    path_and_operation_detail = {'/eog/event_detail/': '查看安全事件{}详情'.format(request.form.get('event_id')),
                                 '/eog/event_suggestion/': '审核{id}事件为{status}'.format(id=request.form.get('id'),
                                                                                      status=request.form.get('status'))
                                 }  # 自定义添加被监测的日志详情说明
    if path in ignore_path:
        return respones

    visitor_id = session.get(current_app.config['VISITOR'])
    referrer = get_user_referrer(request)  # 自定义referer 这里兼容 python直接运行代码与nginx运行代码
    ip = get_user_ip(request)  # 自定义封装获取ip，可以与nginx搭配使用
    user_agent = request.headers.get("User-Agent")  # 获取UA
    url = request.url  # 获取访问的url
    area = ''
    province = ''
    print(ip)
    ip_result = ip2region.lookup(ip=ip)
    if ip_result:  # ip解析地址
        area = ip_result[0] + ':' + ip_result[1]
    # if config.DevelopmentConfig.CMS_USER_ID in session:
    #     operate_log=Operate_Log(realname=g.eog_user.realname, ip=ip, path=path)
    #     if path in path_and_operation_detail.keys():
    #         operate_log.operation=path_and_operation_detail.get(path)
    #     operate_log.save()
    if user_agent:
        user_agent = user_agent[0:500]
    if url:
        url = url[0:500]
    if referrer:
        referrer = referrer[0:500]
    logs = {
        'visitor_id': visitor_id,
        'ip': ip,
        'user_agent': user_agent,
        'path': path,
        'url': url,
        'referrer': referrer,
        'area': area,
        'province': province,
        'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S '),
    }
    from utils import zlcache
    zlcache.hset(key=str(datetime.now()), value=str(logs))
    return respones


@bp.app_errorhandler(404)
def page_not_found(error):
    return render_template('front/front_404.html'), 404


@bp.app_errorhandler(500)
def server_error(error):  # 服务器内部错误
    return render_template('front/front_404.html'), 500
