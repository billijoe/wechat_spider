# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/6/8 11:31
@Auth ： AJay13
@File ：urls.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""

from utils import tools
from . import views


bp = views.bp
# 登录、登出、首页
bp.add_url_rule('login/', view_func=views.LoginView.as_view('login'))  # 后台登录页面
bp.add_url_rule('logout/', view_func=views.LogoutView.as_view('logout'))  # 后台登录页面
bp.add_url_rule('/', view_func=views.IndexView.as_view('index'))  # 后台登录页面

# 统计图
bp.add_url_rule('barChart1/', view_func=views.BarChart1View.as_view('get_bar_chart1'))  # 本周采集统计图
bp.add_url_rule('barChart2/', view_func=views.BarChart2View.as_view('get_bar_chart2'))  # 今日收录文章表
bp.add_url_rule('barChart3/', view_func=views.BarChart3View.as_view('get_bar_chart3'))  # 公众号总文章柱状图
bp.add_url_rule('barChart4/', view_func=views.BarChart4View.as_view('get_bar_chart4'))  # 今日访问量

# 公众号统计图
bp.add_url_rule('readnum_echarts/', view_func=views.ReadEchartsView.as_view('get_bar_readnum'))  # 阅读量统计折线图
bp.add_url_rule('article_hour_echarts/',
                view_func=views.ArticleHourEchartsView.as_view('get_bar_article_hour'))  # 历史发文时间折线图
bp.add_url_rule('mouth_article_echarts/',
                view_func=views.MouthArticleEchartsView.as_view('get_bar_mouth_article'))  # 本月发文折线图
bp.add_url_rule('readnum_echarts_pie/', view_func=views.ReadnumEchartsPieView.as_view('readnum_echarts_pie'))  # 本月发文折线图
bp.add_url_rule('article_hour_num_pie/',
                view_func=views.ArticleHourNumPieView.as_view('article_hour_num_pie'))  # 发文时间扇形图
bp.add_url_rule('article_yuanchuang_pie/',
                view_func=views.ArticleYuanchuangPieView.as_view('article_yuanchuang_pie'))  # 文章原创
bp.add_url_rule('comment_rate/', view_func=views.Comment_RateView.as_view('comment_rate'))  # 评率率
bp.add_url_rule('like_rate/', view_func=views.LikeRateView.as_view('like_rate'))  # 再看率

# 标签模块
bp.add_url_rule('tag_show/', view_func=views.TagShowView.as_view('tag_show'))  # 展示标签
bp.add_url_rule('tag_add/', view_func=views.TagAddView.as_view('tag_add'))  # 添加标签
bp.add_url_rule('tag_edit/', view_func=views.TagEditView.as_view('tag_edit'))  # 编辑标签
bp.add_url_rule('tag_del/', view_func=views.TagDelView.as_view('tag_del'))  # 删除标签

# 社区提交公众号模块
bp.add_url_rule('community_account_show/',
                view_func=views.CommunityAccountShowView.as_view('community_account_show'))  # 展示社区公众号&&模糊查询
bp.add_url_rule('community_account_add/',
                view_func=views.CommunityAccountAddView.as_view('community_account_add'))  # 添加社区公众号
bp.add_url_rule('community_account_edit/',
                view_func=views.CommunityAccountEditView.as_view('community_account_edit'))  # 编辑社区公众号
bp.add_url_rule('community_account_del/',
                view_func=views.CommunityAccountDelView.as_view('community_account_del'))  # 删除社区公众号
bp.add_url_rule('community_account_status/',
                view_func=views.CommunityAccountStatusView.as_view('community_account_status'))  # 编辑社区公众号状态
bp.add_url_rule('community_account_search/',
                view_func=views.CommunityAccountSearchView.as_view('community_account_search'))  # 搜索公众号社区提交
bp.add_url_rule('community_accounts_del/',
                view_func=views.CommunityAccountsDelView.as_view('community_accounts_del'))  # 批量删除公众号

# 公众号任务模块
bp.add_url_rule('account_task_show/', view_func=views.AccountTaskShowView.as_view('account_task_show'))  # 展示公众号任务
bp.add_url_rule('account_task_edit/', view_func=views.AccountTaskEditView.as_view('account_task_edit'))  # 编辑公众号任务
bp.add_url_rule('account_task_del/', view_func=views.AccountTaskDelView.as_view('account_task_del'))  # 删除公众号任务
bp.add_url_rule('account_task_status/',
                view_func=views.AccountTaskStatusView.as_view('account_task_status'))  # 更改公众号任务状态
bp.add_url_rule('account_tasks_start/',
                view_func=views.AccountTasksStartView.as_view('account_tasks_start'))  # 批量监控和公众号任务
bp.add_url_rule('account_tasks_forbid/',
                view_func=views.AccountTasksForbidView.as_view('account_tasks_forbid'))  # 批量停止和公众号任务
bp.add_url_rule('account_synchronization/', view_func=views.AccountSynchronization.as_view('account_synchronization'))  # 同步微信号名称# DO:这里有个bug：模型类中的私有变量无法被调用
bp.add_url_rule('account_a_live_zombie/', view_func=views.AccountALiveZombie.as_view('account_a_live_zombie'))  # 复活僵尸号

# 公众号模块
bp.add_url_rule('account_show/', view_func=views.AccountShowView.as_view('account_show'))  # 展示公众号#DO:这里有个bug：模型类中的私有变量无法被调用
bp.add_url_rule('account_add/', view_func=views.AccountAddView.as_view('account_add'))  # 添加公众号(管理员添加，默认被收录)
bp.add_url_rule('account_del/', view_func=views.AccountDelView.as_view('account_del'))  # 删除公众号
bp.add_url_rule('accounts_del/', view_func=views.AccountsDelView.as_view('accounts_del'))  # 批量删除公众号

# 文章模块
bp.add_url_rule('article_show/', view_func=views.ArticleShowView.as_view('article_show'))  # 展示文章 #DO:这里有个bug：模型类中的私有变量无法被调用
bp.add_url_rule('article_flag/', view_func=views.ArticleFlagView.as_view('article_flag'))  # 文章加精  编辑公众号文章flag
bp.add_url_rule('article_show_one/',
                view_func=views.ArticleShowOneView.as_view('article_show_one'))  # 展示一篇文章
bp.add_url_rule('article_del/', view_func=views.ArticleDelView.as_view('article_del'))  # 删除文章
bp.add_url_rule('articles_del/', view_func=views.ArticlesDelView.as_view('articles_del'))  # 批量删除文章

# Github模块
bp.add_url_rule('remote_github/', view_func=views.RemoteGithubView.as_view('remote_github'))  # 同步github仓库

# 周报模块
bp.add_url_rule('weekly_detail/', view_func=views.WeeklyDetailView.as_view('weekly_detail'))  # 微信周报详情
bp.add_url_rule('wechat_github/', view_func=views.WechatGithubView.as_view('wechat_github'))  # github仓库微信公众号快速关注

# 轮播图模块
bp.add_url_rule('banner_show/', view_func=views.BannerShowView.as_view('banner_show'))  # 轮播图展示
bp.add_url_rule('banner_add/', view_func=views.BannerAddView.as_view('banner_add'))  # 添加轮播图
bp.add_url_rule('banner_edit/', view_func=views.BannerEditView.as_view('banner_edit'))  # 编辑轮播图
bp.add_url_rule('banner_del/', view_func=views.BannerDelView.as_view('banner_del'))  # 删除轮播图

# 日志模块
bp.add_url_rule('user_log/', view_func=views.UserLogView.as_view('user_log'))  # 用户日志展示

# IP黑名单，
bp.add_url_rule('block_ip/', view_func=views.BlockIPView.as_view('block_ip'))  # IP黑名单展示
bp.add_url_rule('add_block_ip/', view_func=views.BlockIPAddView.as_view('add_block_ip'))  # 添加IP黑名单
bp.add_url_rule('del_block_ip/', view_func=views.BlockIPDelView.as_view('del_block_ip'))  # 删除IP黑名单

# 热搜关键字
bp.add_url_rule('hot_search/', view_func=views.HotSearchView.as_view('hot_search'))  # 用户热搜关键字展示
# 展示热搜关键字top，某个时间段
bp.add_url_rule('hot_search_top20/', view_func=views.UserLogView.as_view('hot_search_top20'))  # 用户热搜关键字展示TOP20

# 公告模块
bp.add_url_rule('announcement/', view_func=views.AnnouncementView.as_view('announcement'))  # 公告展示
bp.add_url_rule('announcement_edit/', view_func=views.AnnouncementEditView.as_view('announcement_edit'))  # 公告展示状态编辑

# 留言板
bp.add_url_rule('msg_board/', view_func=views.MsgBoardView.as_view('msg_board'))  # 留言板展示
bp.add_url_rule('msg_board_add/', view_func=views.MsgBoardAddView.as_view('msg_board_add'))  # 留言板添加留言
bp.add_url_rule('msg_board_del/', view_func=views.MsgBoardDelView.as_view('msg_board_del'))  # 留言板删除留言
bp.add_url_rule('msgs_board_del/', view_func=views.MsgsBoardDelView.as_view('msgs_board_del'))  # 留言板批量删除留言

# 系统监控
bp.add_url_rule('monitor/', view_func=views.MonitorView.as_view('monitor'))  # 系统监控

# 系统模块
bp.add_url_rule('system/', view_func=views.SystemView.as_view('system'))  # 系统配置

# 管理员模块
bp.add_url_rule('info/', view_func=views.InfoView.as_view('info'))  # 用户信息

# 可视化大屏
bp.add_url_rule('dashboard/', view_func=views.DashBoardView.as_view('dashboard'))  # 可视化大屏
bp.add_url_rule('dashboard/barChart1/', view_func=views.Echarts1View.as_view('barChart1'))  # 可视化大屏
bp.add_url_rule('dashboard/barChart2/', view_func=views.Echarts2View.as_view('barChart2'))  # 可视化大屏
bp.add_url_rule('dashboard/barChart5/', view_func=views.Echarts5View.as_view('barChart5'))  # 可视化大屏
bp.add_url_rule('dashboard/barChart6/', view_func=views.Echarts6View.as_view('barChart6'))  # 可视化大屏
bp.add_url_rule('dashboard/barChart31/', view_func=views.Echarts31View.as_view('barChart31'))  # 可视化大屏
bp.add_url_rule('dashboard/barChart32/', view_func=views.Echarts32View.as_view('barChart32'))  # 可视化大屏
bp.add_url_rule('dashboard/barChart33/', view_func=views.Echarts33View.as_view('barChart33'))  # 可视化大屏
bp.add_url_rule('dashboard/api/info_num/', view_func=views.InfoNumView.as_view('info_num'))  # 可视化大屏



# 额外功能：模板过滤器、
bp.add_app_template_filter(tools.get_user_ip, 'get_user_ip')  # 模板过滤器 获取用户的ip展示
