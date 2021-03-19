# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from flask import Blueprint
from flask_wtf.csrf import CSRFProtect

# from apis.v1.home import interface_home
# from apis.v1.wechat import interface_article

csrf = CSRFProtect()
api_bp = Blueprint('home', __name__, url_prefix='/api/<version>/')
csrf.exempt(api_bp)
# 所有api的接口管理

# api_bp.add_url_rule('tags/', strict_slashes=False, view_func=interface_home.InterFaceWechtTages.as_view('tags'))
# api_bp.add_url_rule('banners/', strict_slashes=False, view_func=interface_home.InterFaceBanners.as_view('banners'))
# api_bp.add_url_rule('articles/', strict_slashes=False, view_func=interface_home.InterFaceArticles.as_view('articles'))
# api_bp.add_url_rule('search/', strict_slashes=False, view_func=interface_home.InterFaceSearch.as_view('search'))
#
# api_bp.add_url_rule('article/', strict_slashes=False, view_func=interface_article.InterFaceArticle.as_view('article'))
# api_bp.add_url_rule('hot_account/', strict_slashes=False,
#                     view_func=interface_article.InterFaceHotWechat.as_view('hot_account'))

# 登录的接口单独做的
from apis.v1.admin.administrator import interface_login, interface_info
from apis.v1.article import interface_article
from apis.v1.tags import interface_tag
from apis.v1.account import interface_account, interface_account_task, interface_community_account
from apis.v1.user import interface_block_ip, interface_hot_search, interface_msg_board, interface_user_log,interface_email_user
from apis.v1.home import interface_home
from apis.v1.setting import interface_setting

api_bp = Blueprint('api', __name__, url_prefix='/api/<version>/')

api_bp.add_url_rule('login/', strict_slashes=False, view_func=interface_login.InterfaceLogin.as_view('login'))
api_bp.add_url_rule('admin_info/', strict_slashes=False,
                    view_func=interface_info.InterfaceAdminInfo.as_view('admin_info'))
# 主页
api_bp.add_url_rule('count/', strict_slashes=False, view_func=interface_home.InterfaceCount.as_view('count'))
api_bp.add_url_rule('system_info/', strict_slashes=False, view_func=interface_home.InterfaceSystemInfo.as_view('system_info')) # cup memory占有率
api_bp.add_url_rule('top_search/', strict_slashes=False, view_func=interface_home.InterfaceTopSearch.as_view('top_search')) # 今日热搜统计
api_bp.add_url_rule('top_article/', strict_slashes=False, view_func=interface_home.InterfaceTopArticle.as_view('top_article')) # 今日采集文章统计
api_bp.add_url_rule('log_visitor_echarts/', strict_slashes=False, view_func=interface_home.InterfaceLogVisitorEcharts.as_view('log_visitor_echarts')) # 今天访客分布统计


# 文章管理
api_bp.add_url_rule('article_list/', strict_slashes=False,
                    view_func=interface_article.InterfaceArticleList.as_view('article_list'))
api_bp.add_url_rule('article_flag/', strict_slashes=False,
                    view_func=interface_article.InterfaceArticleFlag.as_view('article_flag'))

# 分类管理
api_bp.add_url_rule('tag_list/', strict_slashes=False,
                    view_func=interface_tag.InterFaceWechtTagList.as_view('tag_list'))

# 公众号管理
api_bp.add_url_rule('account_list/', strict_slashes=False,
                    view_func=interface_account.InterfaceAccountList.as_view('account_list'))

# 公众号任务管理
api_bp.add_url_rule('account_task_list/', strict_slashes=False,
                    view_func=interface_account_task.InterfaceAccountTaskList.as_view('account_task_list'))

# 社区提交公众号管理
api_bp.add_url_rule('community_account_list/', strict_slashes=False,
                    view_func=interface_community_account.InterfaceCommunityAccountList.as_view(
                        'community_account_list'))

##用户日志展示
api_bp.add_url_rule('user_log_list/', strict_slashes=False,
                    view_func=interface_user_log.InterfaceUserLogList.as_view('user_log_list')) # 用户日志
api_bp.add_url_rule('hot_search_list/', strict_slashes=False,
                    view_func=interface_hot_search.InterfaceHotSearchList.as_view('hot_search_list'))# 热搜展示
api_bp.add_url_rule('block_ip_list/', strict_slashes=False,
                    view_func=interface_block_ip.InterfaceBlockIPList.as_view('block_ip_list'))# 黑名单
api_bp.add_url_rule('msg_board_list/', strict_slashes=False,
                    view_func=interface_msg_board.InterfaceMsgBoardList.as_view('msg_board_list'))# 留言板信息
api_bp.add_url_rule('email_user_list/', strict_slashes=False,
                    view_func=interface_email_user.InterfaceEmailUserList.as_view('email_user_list')) # email用户
## 设置
api_bp.add_url_rule('email_show/', strict_slashes=False,
                    view_func=interface_setting.InterfaceEmailShow.as_view('email_show'))
api_bp.add_url_rule('email_edit/', strict_slashes=False,
                    view_func=interface_setting.InterfaceEmailEdit.as_view('email_edit'))