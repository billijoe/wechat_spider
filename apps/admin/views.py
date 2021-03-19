# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

import datetime
import re
import time

from flask import (
    Blueprint,
    views,
    render_template,
    session,
    request,
    redirect,
    url_for,
    g,
    current_app
)
from sqlalchemy import and_, func
from sqlalchemy import extract
from sqlalchemy import or_

import config
from exts import db
from models import Admin, WechatTag, TWechatAccount, GitCommit, Banner, TCommunityWechatAccount, \
    Announcement, User_Logs, MsgBoard, BlockIP, HotSearch
from utils import field
from utils import tools
from .decorators import login_required
from .forms import LoginForm, AnnouncementForm, MsgBoardForm
from .models import WechatAccount, WechatAccountTask, WechatArticle, WechatArticleComment, WechatArticleTask, \
    WechatArticleDynamic, WechatArticleList

ip2region = tools.IP2Region()
bp = Blueprint('admin', __name__, url_prefix='/admin/')


class BarChart1View(views.MethodView):
    decorators = [login_required]

    def get(self):
        c = tools.bar_base1()
        return c.dump_options()

    def post(self):
        pass


class BarChart2View(views.MethodView):
    decorators = [login_required]

    def get(self):
        c = tools.bar_base2()
        return c.dump_options()

    def post(self):
        pass


class BarChart3View(views.MethodView):
    decorators = [login_required]

    def get(self):
        c = tools.bar_base3()
        return c.dump_options()

    def post(self):
        pass


class BarChart4View(views.MethodView):
    decorators = [login_required]

    def get(self):
        # 迁移日志redis到mysql数据库
        from utils.tools import synchronization_log
        synchronization_log()
        c = tools.bar_base4()
        return c.dump_options()

    def post(self):
        pass


class ReadEchartsView(views.MethodView):

    def get(self):
        biz = request.args.get('biz')
        c = tools.readnum_echarts(biz=biz)
        return c.dump_options()

    def post(self):
        pass


# 历史发文时间折线图
class ArticleHourEchartsView(views.MethodView):

    def get(self):
        biz = request.args.get('biz')
        c = tools.article_hour_num(biz=biz)
        return c.dump_options()

    def post(self):
        pass


# 本月发文折线图
class MouthArticleEchartsView(views.MethodView):

    def get(self):
        biz = request.args.get('biz')
        c = tools.mouth_article(biz=biz)
        return c.dump_options()

    def post(self):
        pass


# 阅读量分布扇形图0
class ReadnumEchartsPieView(views.MethodView):

    def get(self):
        biz = request.args.get('biz')
        c = tools.readnum_echarts_pie(biz=biz)
        return c.dump_options()

    def post(self):
        pass


class ArticleHourNumPieView(views.MethodView):

    def get(self):
        biz = request.args.get('biz')
        c = tools.article_hour_num_pie(biz=biz)
        return c.dump_options()

    def post(self):
        pass


class ArticleYuanchuangPieView(views.MethodView):

    def get(self):
        biz = request.args.get('biz')
        c = tools.article_yuanchuang_pie(biz=biz)
        return c.dump_options()

    def post(self):
        pass


class Comment_RateView(views.MethodView):

    def get(self):
        biz = request.args.get('biz')
        c = tools.comment_rate(biz=biz)
        return c.dump_options()

    def post(self):
        pass


class LikeRateView(views.MethodView):

    def get(self):
        biz = request.args.get('biz')
        c = tools.like_rate(biz=biz)
        return c.dump_options()

    def post(self):
        pass


# 大屏监控echarts

class Echarts1View(views.MethodView):
    decorators = [login_required]

    def get(self):
        c = tools.echarts_1()

        return field.success(data=c)

    def post(self):
        pass


# 大屏监控echarts

class Echarts2View(views.MethodView):
    decorators = [login_required]

    def get(self):
        c = tools.echarts_2()

        return field.success(data=c)

    def post(self):
        pass


class Echarts5View(views.MethodView):
    decorators = [login_required]

    def get(self):
        c = tools.echarts_5()

        return field.success(data=c)

    def post(self):
        pass


class Echarts6View(views.MethodView):

    def get(self):
        c = tools.echarts_6()

        return field.success(data=c)

    def post(self):
        pass


class Echarts31View(views.MethodView):
    decorators = [login_required]

    def get(self):
        c = tools.echarts_31()

        return field.success(data=c)

    def post(self):
        pass


class Echarts32View(views.MethodView):
    decorators = [login_required]

    def get(self):
        c = tools.echarts_32()

        return field.success(data=c)

    def post(self):
        pass


class Echarts33View(views.MethodView):
    decorators = [login_required]

    def get(self):
        c = tools.echarts_33()

        return field.success(data=c)

    def post(self):
        pass


class InfoNumView(views.MethodView):
    decorators = [login_required]

    def get(self):
        wechat_article_num = WechatArticle.query.count()  # 文章数量
        account_num = TWechatAccount.query.count()  # 微信数量
        context = {
            "wechat_article_num": wechat_article_num,
            "account_num": account_num,
        }
        return field.success(data=context)

    def post(self):
        pass


# 登录页面
class LoginView(views.MethodView):

    def get(self):
        message = request.args.get('message')
        return render_template('admin/login.html', message=message)

    def post(self):
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data  # 邮箱或者用户名
            password = form.password.data
            remember = form.remember.data
            user = Admin.query.filter_by(email=email).first() or Admin.query.filter_by(username=email).first()
            if user and user.check_password(password):
                session[current_app.config['CMS_USER_ID']] = user.id  # 保存用户登录信息
                if remember:
                    # 如果设置session.permanent = True，那么过期时间为31天
                    session.permanent = True
                user.last_login_time = datetime.datetime.now()
                db.session.add(user)
                db.session.commit()
                return field.success(message='登陆成功！')
            else:
                return field.params_error(message='邮箱或者密码错误')

        else:
            message = form.get_error()
            return field.params_error(message=message)


# 后台首页
class IndexView(views.MethodView):
    decorators = [login_required]

    def get(self):  # ajax 10s定时请求一次服务器
        today = datetime.date.today()
        try:  # 当初始化的时候，后台不存在迁移的数据库。
            # if 1==1:
            wechat_article_num = WechatArticle.query.count()  # 文章数量
            account_num = WechatAccount.query.count()  # 微信数量
            comment_num = WechatArticleComment.query.count()  # 微信评论总数量
            article_task_num = WechatArticleTask.query.count()  # 公众号文章爬取任务数量
            to_grab_task_num = WechatArticleTask.query.filter_by(state=0).count()  # 待抓取公众号任务数量
            grabbed_task_num = WechatArticleTask.query.filter_by(state=1).count()  # 抓取完毕任务数量
            grabbing_task_num = WechatArticleTask.query.filter_by(state=2).count()  # 抓取中的任务数量
            contribution_num = TCommunityWechatAccount.query.with_entities(
                TCommunityWechatAccount.founder).distinct().count() - 1  # 贡献者人数总数量 -1位空白的人员
            grabbed_account_task = WechatAccountTask.query.filter(
                and_(extract('year', WechatAccountTask.last_spider_time) == str(today).split('-')[0],
                     extract('month', WechatAccountTask.last_spider_time) == str(today).split('-')[1],
                     extract('day', WechatAccountTask.last_spider_time) == str(today).split('-')[2]),
                WechatAccountTask.is_zombie == 0
            ).count()  # 今日已经采集过的公众号的数量（最后采集日期等于今日）
            account_task = WechatAccountTask.query.filter_by(is_zombie=0).count()  # 非僵尸号的数量
        except Exception as e:
            print(e)
            wechat_article_num = 0
            account_num = 0
            comment_num = 0
            article_task_num = 0
            to_grab_task_num = 0
            grabbing_task_num = 0
            grabbed_task_num = 0
            contribution_num = 0
            account_task = 0
            grabbed_account_task = 0

        b = account_task if account_task != 0 else 1
        loading = "%.2f%%" % (grabbed_account_task / b * 100)
        t_announcement = Announcement.query.filter(Announcement.flag == 1).order_by(
            Announcement.time.desc()).first()  # 公告信息
        t_account_num = TWechatAccount.query.count()  # 添加微信数量
        t_community_account_num = TCommunityWechatAccount.query.count()  # 社区提交公众号数量
        t_community_account = TCommunityWechatAccount.query.filter(
            TCommunityWechatAccount.status == '0').all()  # 社区提交公众号未审核
        t_account_start_num = TWechatAccount.query.filter_by(status='start').count()  # 监控微信数量
        git_commit_num = GitCommit.query.count()  # github同步次数
        context = {
            'announcement': t_announcement,  # 公告展示
            'wechat_article_num': wechat_article_num,  # 微信文章数量
            't_account_num': t_account_num,  # 公众号数量
            't_community_account_num': t_community_account_num,  # 社区提交公众号数量
            'account_num': account_num,  # 有效公众号
            't_account_start_num': t_account_start_num,  # 当前监控微信数量
            'comment_num': comment_num,  # 评论数量
            'git_commit_num': git_commit_num,  # git同步次数
            'article_task_num': article_task_num,  # 公众号文章爬取任务数量
            'to_grab_task_num': to_grab_task_num,  # 待抓取公众号任务数量
            'grabbing_task_num': grabbing_task_num,  # 抓取中的任务数量
            'grabbed_task_num': grabbed_task_num,  # 抓取完毕任务数量
            'contribution_num': contribution_num,  # 参与贡献者的人数数量
            'loading': loading,
            't_community_account': t_community_account,  # 社区提交公众号未审核

        }
        return render_template('admin/admin_index.html', **context)

    def post(self):
        pass


# 注销
class LogoutView(views.MethodView):
    decorators = [login_required]

    def get(self):
        del session[current_app.config['CMS_USER_ID']]
        return redirect(url_for('admin.login'))

    def post(self):
        pass


# 添加标签
class TagAddView(views.MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('admin/tag_add.html')

    def post(self):
        tag_name = request.form.get('tag_name')
        tag_en = request.form.get('tag_en')
        tag_summary = request.form.get('tag_summary')

        tag = WechatTag(tag_name=tag_name, tag_en=tag_en, tag_summary=tag_summary)
        try:
            db.session.add(tag)
            db.session.commit()
            print('标签添加成功{}'.format(tag_name))
            return field.success(message='添加标签成功')
        except Exception as e:
            return field.success(message='标签{}已经存在'.format(tag_name))


# 展示标签
class TagShowView(views.MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('admin/tag_show.html')

    def post(self):
        rule_data = []
        page = int(request.form.get('page'))
        limit = int(request.form.get('limit'))
        start = (page - 1) * limit
        end = start + limit
        tag_obj = WechatTag.query
        tags = tag_obj.slice(start, end)
        total = tag_obj.count()

        for i in tags:
            tag = {}
            tag['id'] = i.id
            tag['tag_name'] = i.tag_name
            tag['tag_en'] = i.tag_en
            tag['tag_summary'] = i.tag_summary
            tag['create_time'] = str(i.create_time)
            rule_data.append(tag)

        return field.layui_success(message='查询成功！', data=rule_data, count=total)


# 编辑标签
class TagEditView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')

        tag = WechatTag.query.get(id)
        if tag:
            tag_name = data.get('tag_name')
            tag_en = data.get('tag_en')
            tag_summary = data.get('tag_summary')
            if tag_name:
                tag.tag_name = tag_name
            if tag_en:
                tag.tag_en = tag_en
            if tag_summary:
                tag.tag_summary = tag_summary
            db.session.commit()
            return field.success(message='修改成功！')
        return field.params_error(message='修改失败！')


# 删除标签
class TagDelView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        tag = WechatTag.query.get(id)
        if tag:
            db.session.delete(tag)
            db.session.commit()
            return field.success(message='删除成功！')
        return field.params_error(message='删除失败！')


# 展示公众号 account_show
class AccountShowView(views.MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('admin/account_show.html')

    def post(self):
        data = request.values
        keys = list(data.keys())
        keys.remove('page')
        keys.remove('limit')

        account_data = []
        page = int(request.form.get('page'))
        limit = int(request.form.get('limit'))
        start = (page - 1) * limit
        end = start + limit
        account_obj = WechatAccount.query
        if keys:
            account_search = account_obj.filter(
                and_(WechatAccount.account.like("%" + data.get('account_name', '') + "%"),
                     )).order_by(
                WechatAccount.spider_time.desc())
        else:
            account_search = account_obj.order_by(WechatAccount.spider_time.desc())
        accounts = account_search.slice(start, end)
        total = account_search.count()
        # 查询所有正在处于监听队列的数据做成字典
        for i in accounts:
            account = {}
            account['id'] = i.id
            account['account_name'] = i.account
            account['account_id'] = getattr(i, '__biz')
            account['head_url'] = i.head_url
            account['summary'] = i.summary
            account['qr_code'] = i.qr_code
            account['verify'] = i.verify
            account['spider_time'] = str(i.spider_time)

            account_data.append(account)

        return field.layui_success(message='查询成功！', data=account_data, count=total)


# 添加公众号 account
class AccountAddView(views.MethodView):
    decorators = [login_required]

    def get(self):
        tags = WechatTag.query.all()
        return render_template('admin/account_add.html', tags=tags)

    def post(self):

        account_id = request.form.get('account_id')
        account_name = request.form.get('account_name')
        tag = request.form.get('tag')
        print(type(account_name), type(tag))
        t_waccount = TCommunityWechatAccount(account_id=account_id,
                                             account_link='https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=#wechat_redirect'.format(
                                                 account_id),
                                             account_name=account_name, tag=int(tag), founder='admin')
        try:
            db.session.add(t_waccount)
            db.session.commit()
            print('公众号添加成功{}'.format(account_name))
            return field.success(message='添加公众号{}成功'.format(account_name))
        except Exception as e:
            print(e)
            return field.success(message='公众号{}已经存在'.format(account_id))


# 删除公众号 account_del
class AccountDelView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        account = WechatAccount.query.get(id)
        if account:
            db.session.delete(account)
            db.session.commit()
            return field.success(message='删除成功！')
        return field.params_error(message='删除失败！')


# 批量删除公众号 accounts_del
class AccountsDelView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        accounts = request.form.get('accounts')
        if accounts:
            for account in eval(accounts):
                # print(account)
                id = account.get('id')
                account = WechatAccount.query.get(id)
                if account:
                    db.session.delete(account)
                    db.session.commit()

            return field.success(message='修改成功！')
        return field.params_error(message='修改失败！')


# 公众号统计 wechat_echarts
@bp.route('wechat_echarts/', methods=['GET'])
def wechat_echarts():
    if request.method == 'GET':

        print(request.args)
        biz = request.args.get('biz')
        if not biz:
            return '缺少参数'

        # 统计信息 公众号、公众号描述、发文总数、平均阅读量、近7天发文、近7天平均阅读量

        wechat_account = WechatAccount.query.filter_by(__biz=biz).first()
        article_sum = WechatArticleList.query.filter_by(__biz=biz).count()
        read_sum = WechatArticleDynamic.query.with_entities(func.sum(WechatArticleDynamic.read_num)).filter_by(
            __biz=biz).scalar()
        read_avg = WechatArticleDynamic.query.with_entities(func.avg(WechatArticleDynamic.read_num)).filter_by(
            __biz=biz).scalar()
        like_avg = WechatArticleDynamic.query.with_entities(func.avg(WechatArticleDynamic.like_num)).filter_by(
            __biz=biz).scalar()
        comment_avg = WechatArticleDynamic.query.with_entities(func.avg(WechatArticleDynamic.comment_count)).filter_by(
            __biz=biz).scalar()
        print(read_avg)
        content = {
            "account": wechat_account.account,
            "qr_code": wechat_account.qr_code,
            "account_biz": wechat_account.__biz,
            "summary": wechat_account.summary,
            "head_url": wechat_account.head_url,
            "article_sum": article_sum,
            "read_sum": read_sum,
            "read_avg": read_avg,
            "like_avg": like_avg,
            "comment_avg": comment_avg,
        }

        return render_template('admin/wechat_echarts.html', **content)


# 展示社区公众号 community_account_show community
class CommunityAccountShowView(views.MethodView):
    decorators = [login_required]

    def get(self):
        tags = WechatTag.query.all()
        return render_template('admin/community_account_show.html', tags=tags)

    def post(self):
        data = request.values
        keys = list(data.keys())
        keys.remove('page')
        keys.remove('limit')
        account_data = []
        page = int(request.form.get('page'))
        limit = int(request.form.get('limit'))
        start = (page - 1) * limit
        end = start + limit
        community_account_obj = TCommunityWechatAccount.query
        if keys:
            account_search = community_account_obj.filter(
                and_(TCommunityWechatAccount.account_name.like("%" + data.get('account', '') + "%"),
                     TCommunityWechatAccount.founder.like("%" + data.get('contributor', '') + "%"),
                     TCommunityWechatAccount.tag.like("%" + data.get('tip', '') + "%"),
                     TCommunityWechatAccount.status.like("%" + data.get('status', '') + "%"))).order_by(
                TCommunityWechatAccount.create_time.desc())
        else:
            account_search = community_account_obj.order_by(TCommunityWechatAccount.create_time.desc())
        community_accounts = account_search.slice(start, end)
        total = account_search.count()
        if total != 0:
            # 查询所有的数据做成字典
            for i in community_accounts:
                accounts = {}
                accounts['id'] = i.id
                accounts['account_name'] = i.account_name
                accounts['account_id'] = i.account_id
                accounts['account_link'] = i.account_link
                accounts['tag_name'] = i.Ctags.tag_name
                accounts['founder'] = i.founder
                accounts['create_time'] = str(i.create_time)
                accounts['status'] = i.status
                account_data.append(accounts)

            return field.layui_success(message='查询成功！', data=account_data, count=total)
        return field.layui_success(message='未查到相关信息', count=0)


# 社区公众号提交 TCommunityWechatAccount
# 添加公众号 community_account
class CommunityAccountAddView(views.MethodView):
    # fix bug 不用添加路由限制
    def post(self):
        account_name = request.form.get('account_name')
        tag_name = request.form.get('tag_name')
        account_link = request.form.get('account_link')  # 实际传入的是一个链接
        founder = request.form.get('founder')
        graph_captcha = request.form.get('graph_captcha')  # 校验验证码
        print(graph_captcha)
        from utils import zlcache
        graph_captcha_mem = zlcache.get(graph_captcha.lower())
        if not graph_captcha_mem:
            return field.params_error(message='请输入正确的验证码')
        else:
            zlcache.delete(graph_captcha.lower())
        # 判断 account_id 我们允许提交的内容为 带有biz的公众号的文章或者公众号的二维码 链接
        pattern = '__biz=(.*?)=='
        new_account_id = re.findall(pattern=pattern, string=account_link)
        if new_account_id:
            if TWechatAccount.query.filter_by(account_id=new_account_id[0] + '==').first():
                return field.params_error(message='公众号{}已经被提交'.format(account_name))
            t_waccount = TCommunityWechatAccount(account_id=new_account_id[0] + '==', account_link=account_link,
                                                 account_name=account_name, tag=tag_name, founder=founder)
            try:
                db.session.add(t_waccount)
                db.session.commit()
                print('社区公众号添加成功{}'.format(account_name))
                return field.success(message='添加公众号{}成功'.format(account_name))
            except Exception as e:
                print(e)
                return field.params_error(message='公众号{}已经存在'.format(account_name))
        return field.params_error(message='{}不是一个有效的链接'.format(account_link))


# 编辑社区公众号 community_account_edit community_account
class CommunityAccountEditView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        account_name = data.get('account_name')
        account_id = data.get('account_id')
        tag_name = data.get('tag_name')
        founder = data.get('founder')
        community_account = TCommunityWechatAccount.query.get(id)
        if community_account:
            if account_name:
                community_account.account_name = account_name
            if account_id:
                community_account.account_id = account_id
            if tag_name:
                community_account.tag = (WechatTag.query.filter_by(tag_name=tag_name).first()).id
            if founder:
                community_account.founder = founder
                # account_tasks.founder = founder
            db.session.commit()
            return field.success(message='修改成功！')
        return field.params_error(message='修改失败！')


# 删除社区公众号 community_account_del
class CommunityAccountDelView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        community_account = TCommunityWechatAccount.query.get(id)
        if community_account:
            # 从监控的任务队列中移除
            db.session.delete(community_account)
            db.session.commit()
            return field.success(message='删除成功！')
        return field.params_error(message='删除失败！')


# 编辑社区公众号状态 community_account_status
class CommunityAccountStatusView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        status = data.get('status')
        community_account = TCommunityWechatAccount.query.get(id)
        if community_account:
            if community_account.status != status:
                community_account.status = status
                # account_tasks.founder = founder
                account_name = community_account.account_name
                account_id = community_account.account_id
                if status == 'premit':
                    # 同意加入到微信库
                    t_waccount = TWechatAccount(account_id=community_account.account_id, account_name=account_name,
                                                tag=community_account.tag)
                    try:
                        db.session.add(t_waccount)
                        db.session.commit()
                        # print('公众号收录成功{}'.format(account_name))
                        return field.success(message='添加公众号{}成功'.format(account_name))
                    except Exception as e:
                        print(e)
                        return field.params_error(message='公众号{}已经存在,收录失败'.format(account_id))
                elif status == 'forbid':
                    # 从微信库中移除
                    try:

                        rm_account_task = TWechatAccount.query.filter_by(account_id=account_id).first()
                        db.session.delete(rm_account_task)
                        db.session.commit()
                        return field.success(message='弃用公众号{}！'.format(account_name))
                    except Exception as e:
                        db.session.commit()
                        return field.success(message='接口错误{}！'.format(account_name))
            return field.params_error(message='已经被被人修改，刷新看看！！')
        return field.params_error(message='修改失败！')


# 查找社区公众号
class CommunityAccountSearchView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        print(data)
        keys = list(data.keys())
        keys.remove('page')
        keys.remove('limit')
        print(keys)
        if keys:
            account_data = []

            page = int(request.form.get('page'))
            limit = int(request.form.get('limit'))
            start = (page - 1) * limit
            account_obj = TCommunityWechatAccount.query
            account_search = account_obj.filter(
                and_(TCommunityWechatAccount.account_name.like("%" + data.get('account', '') + "%"),
                     TCommunityWechatAccount.founder.like("%" + data.get('contributor', '') + "%"),
                     TCommunityWechatAccount.tag.like("%" + data.get('tip', '') + "%"),
                     TCommunityWechatAccount.status.like("%" + data.get('status', '') + "%")))
            print('查询结果', account_search.first())
            print('查询结果', account_search.count())
            # if 'account' in keys:
            #     account_search = account_obj.filter(
            #         TCommunityWechatAccount.account_name.like("%" + data.get('account') + "%"))
            # elif 'contributor' in keys:
            #     account_search = account_obj.filter(
            #         TCommunityWechatAccount.founder.like("%" + data.get('contributor') + "%"))
            # elif 'tip' in keys:
            #     account_search = account_obj.filter(TCommunityWechatAccount.tag == data.get('tip'))
            # elif 'status' in keys:
            #     account_search = account_obj.filter(TCommunityWechatAccount.status == data.get('status'))
            # else:
            #     account_search = account_obj.filter()
            count = account_search.count()
            account = account_search.slice(start, start + limit)
            if count != 0:
                for i in account:
                    accounts = {}
                    accounts['id'] = i.id
                    accounts['account_name'] = i.account_name
                    accounts['account_id'] = i.account_id
                    accounts['account_link'] = i.account_link
                    accounts['tag_name'] = i.Ctags.tag_name
                    accounts['founder'] = i.founder
                    accounts['create_time'] = str(i.create_time)
                    accounts['status'] = i.status
                    account_data.append(accounts)
                return field.layui_success(message='查询成功！', data=account_data, count=count)
            else:
                return field.layui_success(message='未查到相关信息', count=0)
        return field.layui_success(message='未查到相关信息', count=0)


# 批量删除公众号 del_accounts
class CommunityAccountsDelView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        ids = request.form.get('id').split(',')
        if ids:
            for id in ids:
                community_account = TCommunityWechatAccount.query.get(id)
                if community_account:
                    # 从监控的任务队列中移除
                    db.session.delete(community_account)
                    db.session.commit()
            return field.success(message='删除成功！')
        return field.params_error(message='删除失败！')


# 展示公众号任务 account_task_show
class AccountTaskShowView(views.MethodView):
    decorators = [login_required]

    def get(self):
        tags = WechatTag.query.all()
        return render_template('admin/account_task_show.html', tags=tags)

    def post(self):
        data = request.values
        keys = list(data.keys())
        keys.remove('page')
        keys.remove('limit')
        account_task_data = []
        page = int(request.form.get('page'))
        limit = int(request.form.get('limit'))
        start = (page - 1) * limit
        end = start + limit

        account_task_obj = TWechatAccount.query
        if keys:
            account_task_search = account_task_obj.filter(
                and_(TWechatAccount.account_name.like("%" + data.get('account_name', '') + "%"),
                     TWechatAccount.account_id.like("%" + data.get('account_id', '') + "%"),
                     TWechatAccount.tag.like("%" + data.get('tip', '') + "%"),
                     TWechatAccount.status.like("%" + data.get('status', '') + "%"))).order_by(
                TWechatAccount.create_time.desc())
        else:
            account_task_search = account_task_obj.order_by(TWechatAccount.create_time.desc())
        account_tasks = account_task_search.slice(start, end)
        total = account_task_search.count()
        # 查询所有正在处于监听队列的数据做成字典
        for i in account_tasks:
            wat = WechatAccountTask.query.filter_by(__biz=i.account_id).first()
            last_publish_time = ''
            last_spider_time = ''
            is_zombie = '未知'
            if wat:
                last_publish_time = str(wat.last_publish_time)
                last_spider_time = str(wat.last_spider_time)
                is_zombie = wat.is_zombie
            task = {}
            task['id'] = i.id
            task['account_name'] = i.account_name
            task['account_id'] = i.account_id
            task['tag_name'] = i.tags.tag_name
            task['founder'] = 'admin'
            task['create_time'] = str(i.create_time)
            task['last_publish_time'] = last_publish_time
            task['last_spider_time'] = last_spider_time
            task['is_zombie'] = is_zombie
            task['status'] = i.status

            account_task_data.append(task)

        return field.layui_success(message='查询成功！', data=account_task_data, count=total)


# 编辑公众号任务 account_task_edit
class AccountTaskEditView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        account_name = data.get('account_name')
        account_id = data.get('account_id')
        tag_name = data.get('tag_name')
        account_tasks = TWechatAccount.query.get(id)
        if account_tasks:
            if account_name:
                account_tasks.account_name = account_name
            if account_id:
                account_tasks.account_id = account_id
            if tag_name:
                account_tasks.tag = (WechatTag.query.filter_by(tag_name=tag_name).first()).id
                # account_tasks.founder = founder
            db.session.commit()
            return field.success(message='修改成功！')
        return field.params_error(message='修改失败！')


# 删除公众号任务 account_task_del
class AccountTaskDelView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        account_id = data.get('account_id')
        print(account_id)
        account = TWechatAccount.query.get(id)
        account_tasks = WechatAccountTask.query.filter_by(__biz=account_id).first()
        # TODO:优化逻辑
        if account:
            # 从监控的任务队列中移除
            db.session.delete(account)
            db.session.commit()
        if account_tasks:
            db.session.delete(account_tasks)
            db.session.commit()
            return field.success(message='删除成功！')
        return field.params_error(message='删除失败！')


# 编辑公众号任务状态 account_task_status
class AccountTaskStatusView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        account_id = data.get('account_id')
        status = data.get('status')
        account_tasks = TWechatAccount.query.get(id)
        if account_tasks:
            if status:
                # account_tasks.founder = founder
                if status == 'start':
                    account_tasks.status = status
                    # 加入到监控任务中
                    add_account_task = WechatAccountTask(__biz=account_id)
                    db.session.add(add_account_task)
                elif status == 'forbid':
                    account_tasks.status = status
                    # 从监控的任务中移除
                    rm_account_task = WechatAccountTask.query.filter_by(__biz=account_id).first()
                    db.session.delete(rm_account_task)
            db.session.commit()
            return field.success(message='修改成功！')
        return field.params_error(message='修改失败！')


# 批量监控公众号任务 account_tasks_start
class AccountTasksStartView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        accounts = request.form.get('accounts')
        if accounts:
            for account in eval(accounts):
                # print(account)
                id = account.get('id')
                account_id = account.get('account_id')
                status = account.get('status')
                account_tasks = TWechatAccount.query.get(id)
                if account_tasks:
                    if status == 'forbid':
                        account_tasks.status = 'start'
                        # 加入到监控任务中
                        try:
                            add_account_task = WechatAccountTask(__biz=account_id)
                            db.session.add(add_account_task)
                            db.session.commit()
                        except:
                            pass
            return field.success(message='修改成功！')
        return field.params_error(message='修改失败！')


# 批量监控公众号任务 account_tasks_forbid
class AccountTasksForbidView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        accounts = request.form.get('accounts')
        if accounts:
            for account in eval(accounts):
                # print(account)
                id = account.get('id')
                account_id = account.get('account_id')
                status = account.get('status')
                account_tasks = TWechatAccount.query.get(id)
                if account_tasks:
                    if status == 'start':
                        account_tasks.status = 'forbid'
                        # 从监控的任务中移除
                        try:
                            rm_account_task = WechatAccountTask.query.filter_by(__biz=account_id).first()
                            db.session.delete(rm_account_task)
                            db.session.commit()
                        except:
                            pass
            return field.success(message='修改成功！')
        return field.params_error(message='修改失败！')


# 同步微信号名称 account_synchronization
class AccountSynchronization(views.MethodView):
    '''
    同步微信号名称。利用采集到的微信信息，同步社区提交的微信的名称与微信任务中的名称
    '''
    decorators = [login_required]

    def get(self):
        return

    def post(self):
        wechat_account = WechatAccount.query.all()
        accounts_dict = {}
        for account in wechat_account:
            accounts_dict[getattr(account, '__biz')] = account.account
            # 同步文章公众号名称:将所有公众号文章中id相等且名称不等的 ，更新名称
            for _ in WechatArticle.query.filter(getattr(WechatArticle, '__biz') == getattr(account, '__biz'),
                                                WechatArticle.account != account.account).all():
                _.account = account.account
        db.session.commit()
        # 同步社区微信名
        t_community_wechat_account = TCommunityWechatAccount.query.all()
        for _ in t_community_wechat_account:
            print(_)
            if accounts_dict.get(_.account_id):
                _.account_name = accounts_dict.get(_.account_id)

        db.session.commit()
        # 同步任务公众号名称
        for _ in TWechatAccount.query.all():
            if accounts_dict.get(_.account_id):
                _.account_name = accounts_dict.get(_.account_id)

        db.session.commit()

        return field.success(message='同步成功！')


# 复活僵尸号 account_a_live
class AccountALiveZombie(views.MethodView):
    '''
    复活僵尸号，将任务中僵尸号1置位0
    '''
    decorators = [login_required]

    def get(self):
        return

    def post(self):
        for _ in WechatAccountTask.query.filter(WechatAccountTask.is_zombie == 1).all():
            _.is_zombie = 0
        db.session.commit()
        return field.success(message='复活成功！')
        # return field.params_error(message='修改失败！')


# 展示文章 article_show article
class ArticleShowView(views.MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('admin/article_show.html')

    def post(self):
        data = request.values
        keys = list(data.keys())
        keys.remove('page')
        keys.remove('limit')
        article_data = []
        page = int(request.form.get('page'))
        limit = int(request.form.get('limit'))
        start = (page - 1) * limit
        end = start + limit

        article_obj = WechatArticle.query
        if keys:
            if 'date_end' in keys:
                article_obj = article_obj.filter(WechatArticle.publish_time < data.get('date_end'))
            if 'date_start' in keys:
                article_obj = article_obj.filter(WechatArticle.publish_time > data.get('date_start'))
            if 'flag' in keys:
                article_obj = article_obj.filter(WechatArticle.flag == int(data.get('flag')))
            article_search = article_obj.filter(
                and_(WechatArticle.account.like("%" + data.get('account_name', '') + "%"),
                     WechatArticle.title.like("%" + data.get('title', '') + "%"),
                     )).order_by(
                WechatArticle.publish_time.desc())
        else:
            article_search = article_obj.order_by(WechatArticle.publish_time.desc())

        articles = article_search.slice(start, end)
        total = article_search.count()
        # 查询所有正在处于监听队列的数据做成字典
        for i in articles:
            # 查询是否原创：时间上可能会比较慢，看下线上情况
            wal = WechatArticleList.query.filter(WechatArticleList.sn == i.sn).first()
            if wal:
                if wal.copyright_stat == 11:
                    copyright_stat = '原创'
                elif wal.copyright_stat == 100 or wal.copyright_stat == 101:
                    copyright_stat = '未声明'
                elif wal.copyright_stat == 201:
                    copyright_stat = '转载'
                else:
                    copyright_stat = wal.copyright_stat
                del_flag = wal.copyright_stat
            else:
                copyright_stat = '未知'
                del_flag = '未知'

            article = {}
            article['id'] = i.id
            article['account'] = i.account
            article['title'] = i.title
            article['url'] = i.url
            article['author'] = i.author
            article['digest'] = i.digest
            article['cover'] = i.cover
            # article['content_html'] = filter_html(i.content_html)  # 做处理
            article['copyright_stat'] = copyright_stat
            article['del_flag'] = del_flag
            article['source_url'] = i.source_url
            article['comment_id'] = i.comment_id
            article['publish_time'] = str(i.publish_time)
            article['spider_time'] = str(i.spider_time)
            article['flag'] = i.flag
            article['__biz'] = getattr(i, '__biz')

            article_data.append(article)

        return field.layui_success(message='查询成功！', data=article_data, count=total)


# 编辑公众号文章flag article_flag
# 如果flag=1 精华文章。else 普通文章
class ArticleFlagView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        flag = data.get('flag')
        wechat_article = WechatArticle.query.get(id)
        if wechat_article:
            if wechat_article.flag != flag:
                wechat_article.flag = flag
                db.session.commit()
                return field.success(message='文章：“{}”修改成功！'.format(wechat_article.title))
                # account_tasks.founder = founder

            return field.params_error(message='已经被被人修改，刷新看看！！')
        return field.params_error(message='修改失败！')


# 展示一篇文章 article_show_one article
class ArticleShowOneView(views.MethodView):
    decorators = [login_required]

    def get(self):
        return field.method_error(message='请求方式错误')

    def post(self):
        id = request.form.get('id')
        article = WechatArticle.query.filter_by(id=id).first()
        content_html = tools.filter_html(article.content_html)  # 做处理
        return field.success(message='查询成功！', data=content_html, )


# 删除文章 article_del
class ArticleDelView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        article = WechatArticle.query.get(id)
        if article:
            db.session.delete(article)
            db.session.commit()
            return field.success(message='删除成功！')
        return field.params_error(message='删除失败！')


# 批量删除文章 articles_del
class ArticlesDelView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        accounts = request.form.get('accounts')
        if accounts:
            for account in eval(accounts):
                # print(account)
                id = account.get('id')
                article = WechatArticle.query.get(id)
                if article:
                    try:
                        db.session.delete(article)
                        db.session.commit()
                    except:
                        pass
                    return field.success(message='删除成功！')
        return field.params_error(message='删除失败！')


# 同步github仓库 remote_github
class RemoteGithubView(views.MethodView):
    decorators = [login_required]

    def get(self):
        commit_logs = GitCommit.query.order_by(GitCommit.create_time.desc()).limit(10).all()
        return render_template('admin/remote_github.html', commit_logs=commit_logs)

    def post(self):

        'Todo:从数据库中setting获取仓库的地址'
        commit_log = request.form.get('commit_log')
        if tools.do_work(commit_log):
            try:
                add_commit = GitCommit(commit_log=commit_log)
                db.session.add(add_commit)
                db.session.commit()

                return field.success(message='同步github成功')
            except Exception as e:
                'TODO:如果同步失败，失败的原因极有可能是因为存在冲突。解决冲突的最好的办法就是删除原来的仓库，然后再试试'

                return field.success(message='同步github失败')


# 周报模块 weekly_detail
class WeeklyDetailView(views.MethodView):
    decorators = [login_required]

    def get(self):
        dayOfWeek = datetime.datetime.now().isocalendar()
        year = dayOfWeek[0]  # 今年的年份
        week = int(dayOfWeek[1])

        week_day = time.strptime('{year}-{week}-{Default_WEEKLY}'.format(year=year, week=int(week) - 1,
                                                                         Default_WEEKLY=config.base_config.Default_WEEKLY),
                                 '%Y-%U-%w')
        wechat_article = WechatArticle.query.filter(WechatArticle.flag == 1).filter(
            and_(extract('year', WechatArticle.publish_time) == year,
                 extract('week', WechatArticle.publish_time) == int(week) - 1,
                 )).order_by(WechatArticle.publish_time.desc()).all()  #

        content = tools.weekily_work(year=year, week=week, week_day=week_day, wechat_article=wechat_article)  # 周报排版
        return render_template('admin/admin_weekly_detail.html', content=content)

    def post(self):
        '''
        传入数据的格式：日期  | 关键字
        :return: 日期返回本周的数据。关键字返回关键字数据。
        '''
        data = request.values
        date_week = data.get('date_week')
        keyword = data.get('keyword')
        if date_week:
            post_date = ((time.strptime(date_week, '%Y-%m-%d')))
            year = int(time.strftime("%Y", post_date))
            week = (int(time.strftime("%W", post_date)) + 1)
            week_day = time.strptime('{year}-{week}-{Default_WEEKLY}'.format(year=year, week=int(week) - 1,
                                                                             Default_WEEKLY=config.base_config.Default_WEEKLY),
                                     '%Y-%U-%w')
            wechat_article = WechatArticle.query.filter(WechatArticle.flag == 1).filter(
                and_(extract('year', WechatArticle.publish_time) == year,
                     extract('week', WechatArticle.publish_time) == int(week) - 1,
                     )).order_by(WechatArticle.publish_time.desc()).all()  #

            content = tools.weekily_work(year=year, week=week, week_day=week_day, wechat_article=wechat_article)  # 周报排版
        else:
            # TODO：关键字报告查询结果展示
            '''传入的只有关键字'''
            if keyword:

                if "&" in keyword:
                    # 将查找关键字变为多条件合并查找；&分割关键字
                    keyword_list = keyword.split('&')
                    article_obj = WechatArticle.query
                    all_filter = []
                    for per_keyword in keyword_list:
                        find_filter = []
                        per_keyword = per_keyword.strip()
                        find_filter.append(WechatArticle.title.like("%" + per_keyword + "%"))
                        find_filter.append(WechatArticle.author.like("%" + per_keyword + "%"))
                        find_filter.append(WechatArticle.account.like("%" + per_keyword + "%"))
                        find_filter.append(WechatArticle.digest.like("%" + per_keyword + "%"))
                        all_filter.append(or_(*find_filter))
                    article_obj = article_obj.filter(and_(*all_filter))
                    article_obj = article_obj.order_by(WechatArticle.publish_time.desc())
                else:

                    # 将查找关键字变为多条件或查找；|分割关键字
                    keyword_list = keyword.split('|')
                    find_filter = []
                    for per_keyword in keyword_list:
                        per_keyword = per_keyword.strip()
                        find_filter.append(WechatArticle.title.like("%" + per_keyword + "%"))
                        find_filter.append(WechatArticle.author.like("%" + per_keyword + "%"))
                        find_filter.append(WechatArticle.account.like("%" + per_keyword + "%"))
                        find_filter.append(WechatArticle.digest.like("%" + per_keyword + "%"))

                    article_obj = WechatArticle.query.filter(or_(*find_filter
                                                                 )).order_by(WechatArticle.publish_time.desc())

                wechat_article = article_obj.all()

            content = tools.weekily_work(year=None, week=None, week_day=None, wechat_article=wechat_article,
                                         keyword=keyword)

        return field.success(data=content)


# github仓库微信公众号快速关注 wechat_github
class WechatGithubView(views.MethodView):
    decorators = [login_required]

    def post(self):
        content = tools.follow_wechat()
        return field.success(data=content)


# 轮播图管理 banner
class BannerShowView(views.MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('admin/banner_show.html')

    def post(self):
        banner_data = []
        page = int(request.form.get('page'))
        limit = int(request.form.get('limit'))
        start = (page - 1) * limit
        end = start + limit
        banner_obj = Banner.query.order_by(Banner.priority.desc())
        banners = banner_obj.slice(start, end)
        total = banner_obj.count()
        # 查询所有正在处于监听队列的数据做成字典
        for i in banners:
            banner = {}
            banner['id'] = i.id
            banner['name'] = i.name
            banner['image_url'] = i.image_url
            banner['link_url'] = i.link_url
            banner['priority'] = i.priority
            banner['create_time'] = str(i.create_time)

            banner_data.append(banner)

        return field.layui_success(message='查询成功！', data=banner_data, count=total)


# 添加轮播图  banner_add
class BannerAddView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        name = request.form.get('name')
        image_url = request.form.get('image_url')
        link_url = request.form.get('link_url')
        priority = request.form.get('priority')
        create_time = request.form.get('create_time')

        a_banner = Banner(name=name, image_url=image_url, link_url=link_url, priority=priority, create_time=create_time)
        try:
            db.session.add(a_banner)
            db.session.commit()
            print('轮播图添加成功{}'.format(name))
            return field.success(message='添加轮播图{}成功'.format(name))
        except Exception as e:
            return field.success(message='id{}已经存在'.format(name))


# 编辑轮播图  banner_edit
class BannerEditView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        name = data.get('name')
        image_url = data.get('image_url')
        link_url = data.get('link_url')
        priority = data.get('priority')
        banner = Banner.query.get(id)
        if banner:
            if name:
                banner.name = name
            if image_url:
                banner.image_url = image_url
            if link_url:
                banner.link_url = link_url
            if priority:
                banner.priority = priority
                # account_tasks.founder = founder
            db.session.commit()
            return field.success(message='修改成功！')
        return field.params_error(message='修改失败！')


# 删除轮播图 banner_del
class BannerDelView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        banner = Banner.query.get(id)
        if banner:
            db.session.delete(banner)
            db.session.commit()
            return field.success(message='删除成功！')
        return field.params_error(message='删除失败！')


# 公告内容
class AnnouncementView(views.MethodView):
    decorators = [login_required]

    def get(self):
        annocuncements = Announcement.query.order_by(Announcement.time.desc()).all()

        return render_template('admin/admin_announcement.html', annocuncements=annocuncements)

    def post(self):
        form = AnnouncementForm(request.form)
        if form.validate():
            title = request.form.get('title')
            content = request.form.get('content')
            announcement = Announcement(title=title, publisher=g.user.id, context=content, flag=1)

            db.session.add(announcement)
            db.session.commit()
            return field.success(message='发布成功')
        else:
            message = form.get_error()
            return field.params_error(message=message)


# 公告编辑 flag
class AnnouncementEditView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):

        data = request.values
        id = data.get('id')
        flag = data.get('flag')
        announcement = Announcement.query.get(id)
        if announcement:
            if announcement.flag != flag:
                announcement.flag = flag
                db.session.commit()
                return field.success(message='公告状态修改成功！')
                # account_tasks.founder = founder

            return field.params_error(message='已经被被人修改，刷新看看！！')
        return field.params_error(message='修改失败！')


# 留言板内容
class MsgBoardView(views.MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('admin/admin_msgboard.html')

    def post(self):
        data = request.values
        keys = list(data.keys())
        keys.remove('page')
        keys.remove('limit')
        amsg_board_data = []
        page = int(request.form.get('page'))
        limit = int(request.form.get('limit'))
        start = (page - 1) * limit
        end = start + limit

        msg_board_obj = MsgBoard.query
        if keys:
            msg_board_search = msg_board_obj.filter(
                and_(MsgBoard.visitor_id.like("%" + data.get('visitor_id', '') + "%"),
                     MsgBoard.ip.like("%" + data.get('ip', '') + "%"),
                     MsgBoard.area.like("%" + data.get('area', '') + "%"),
                     MsgBoard.content.like("%" + data.get('content', '') + "%"))).order_by(
                MsgBoard.create_time.desc())
        else:
            msg_board_search = msg_board_obj.order_by(MsgBoard.create_time.desc())
        msgs = msg_board_search.slice(start, end)
        total = msg_board_search.count()
        # 查询所有正在处于监听队列的数据做成字典
        for i in msgs:
            task = {}
            task['id'] = i.id
            task['visitor_id'] = i.visitor_id
            task['ip'] = i.ip
            task['content'] = i.content
            task['area'] = i.area
            task['create_time'] = str(i.create_time)

            amsg_board_data.append(task)

        return field.layui_success(message='查询成功！', data=amsg_board_data, count=total)


# 留言添加 msg_board_add
class MsgBoardAddView(views.MethodView):

    def get(self):
        return

    def post(self):
        form = MsgBoardForm(request.form)
        if form.validate():
            content = form.content.data
            visitor_id = session.get(current_app.config['VISITOR'])
            ip = tools.get_user_ip(request)
            ip_result = ip2region.lookup(ip=ip)
            area = ''
            if ip_result:  # ip解析地址
                area = ip_result[0] + ':' + ip_result[1]
            msg = MsgBoard(content=content, ip=ip, area=area, visitor_id=visitor_id)
            db.session.add(msg)
            db.session.commit()
            return field.success(message='留言成功')
        else:
            message = form.get_error()
            return field.params_error(message=message)


# 留言板删除留言 msg_board_del
class MsgBoardDelView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        msg = MsgBoard.query.get(id)
        if msg:
            db.session.delete(msg)
            db.session.commit()
            return field.success(message='删除成功！')
        return field.params_error(message='删除失败！')


# 留言板批量删除留言 msgs_board_del
class MsgsBoardDelView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        msgs = request.form.get('msgs')
        if msgs:
            for _ in eval(msgs):
                id = _.get('id')
                msg = MsgBoard.query.get(id)
                if msg:
                    try:
                        db.session.delete(msg)
                        db.session.commit()
                    except:
                        pass
            return field.success(message='删除成功！')
        return field.params_error(message='删除失败！')


# 系统设置
class MonitorView(views.MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('admin/monitor.html')


# 系统设置
class SystemView(views.MethodView):
    decorators = [login_required]

    def get(self):
        import config
        # annocuncements = Announcement.query.order_by(Announcement.time.desc()).all()
        system = {
            "weekly": config.base_config.Default_WEEKLY,
            "year": config.base_config.Default_YEAR,
        }
        return render_template('admin/admin_system.html', system=system)

    def post(self):
        pass


# 用户信息
class InfoView(views.MethodView):
    decorators = [login_required]

    def get(self):
        # annocuncements = Announcement.query.order_by(Announcement.time.desc()).all()
        info = ''
        return render_template('admin/admin_info.html', info=info)

    def post(self):
        pass


# 可视化大屏
class DashBoardView(views.MethodView):
    decorators = [login_required]

    def get(self):
        wechat_article_num = WechatArticle.query.count()  # 文章数量
        account_num = TWechatAccount.query.count()  # 微信数量
        print(account_num)
        return render_template('admin/dashboard.html', wechat_article_num=wechat_article_num, account_num=account_num)

    def post(self):
        pass


# 用户日志
class UserLogView(views.MethodView):
    decorators = [login_required]

    def get(self):
        # annocuncements = Announcement.query.order_by(Announcement.time.desc()).all()
        from utils.tools import synchronization_log
        synchronization_log()
        info = ''
        return render_template('admin/user_logs.html', info=info)

    def post(self):
        data = request.values
        keys = list(data.keys())
        keys.remove('page')
        keys.remove('limit')
        logs_data = []
        page = int(request.form.get('page'))
        limit = int(request.form.get('limit'))
        start = (page - 1) * limit
        end = start + limit
        logs_obj = User_Logs.query
        if keys:  # TODO: 未做设备分类
            logs_search = logs_obj.filter(
                and_(User_Logs.visitor_id.like("%" + data.get('ID', '') + "%"),
                     User_Logs.ip.like("%" + data.get('ip', '') + "%"),
                     User_Logs.area.like("%" + data.get('area', '') + "%"),
                     )).order_by(
                User_Logs.create_time.desc())
        else:
            logs_search = logs_obj.order_by(User_Logs.create_time.desc())
        logs = logs_search.slice(start, end)
        total = logs_search.count()
        # 查询所有正在处于监听队列的数据做成字典
        for i in logs:
            log = {}
            log['id'] = i.id
            log['visitor_id'] = i.visitor_id
            log['user_agent'] = i.user_agent
            log['path'] = i.path
            log['url'] = i.url
            log['referrer'] = i.referrer
            log['ip'] = i.ip
            log['area'] = i.area
            log['create_time'] = str(i.create_time)
            UA = tools.get_user_driver(i.user_agent)
            log['device'] = str(UA)
            log['device_logo'] = tools.get_driver_logo(UA)
            logs_data.append(log)

        return field.layui_success(message='查询成功！', data=logs_data, count=total)


# IP黑名单
class BlockIPView(views.MethodView):
    decorators = [login_required]

    def get(self):

        return render_template('admin/block_ip.html')

    def post(self):
        data = request.values
        keys = list(data.keys())
        keys.remove('page')
        keys.remove('limit')
        ips_data = []
        page = int(request.form.get('page'))
        limit = int(request.form.get('limit'))
        start = (page - 1) * limit
        end = start + limit
        block_ip_obj = BlockIP.query
        if keys:
            block_ip_search = block_ip_obj.filter(
                and_(
                    BlockIP.ip.like("%" + data.get('ip', '') + "%"),

                )).order_by(
                BlockIP.create_time.desc())
        else:
            block_ip_search = block_ip_obj.order_by(BlockIP.create_time.desc())
        # 查询的时间为大于  现在的时间-黑名单周期时间(只显示现在还在黑名单的数据)
        # live_time = (datetime.datetime.now()+datetime.timedelta(seconds=-config.base_config.BLOCK_IP_TIMEOUT)).strftime("%Y-%m-%d %H:%M:%S")
        # block_ips = block_ip_search.filter(BlockIP.create_time>live_time).slice(start, end)
        block_ips = block_ip_search.slice(start, end)
        total = block_ip_search.count()

        for i in block_ips:
            data_dict = {}
            data_dict['id'] = i.id
            data_dict['ip'] = i.ip
            data_dict['notes'] = i.notes
            data_dict['create_time'] = str(i.create_time)
            data_dict['end_time'] = str(i.end_time)
            data_dict['time'] = int(time.mktime(time.strptime(str(i.end_time), "%Y-%m-%d %H:%M:%S"))) * 1000
            print(data_dict['time'])
            ips_data.append(data_dict)

        return field.layui_success(message='查询成功！', data=ips_data, count=total)


# 添加IP黑名单 add_block_ip
class BlockIPAddView(views.MethodView):
    decorators = [login_required]

    def post(self):
        ip = request.form.get('ip')
        notes = request.form.get('notes')

        from utils.zlcache import ipset, ipget

        if ipget(ip):
            return field.params_error(message='{ip}已经处于黑名单'.format(ip=ip))
        ipset(ip, ip)
        # end_time = 现在时间 加上黑名单时间
        end_time = (datetime.datetime.now() + datetime.timedelta(seconds=config.base_config.BLOCK_IP_TIMEOUT)).strftime(
            "%Y-%m-%d %H:%M:%S")
        add_block_ip = BlockIP(ip=ip, notes=notes, end_time=end_time)
        db.session.add(add_block_ip)
        db.session.commit()
        return field.success(message='添加{}到黑名单'.format(ip))


# 删除IP黑名单 del_block_ip
class BlockIPDelView(views.MethodView):
    decorators = [login_required]

    def get(self):
        pass

    def post(self):
        data = request.values
        id = data.get('id')
        block_ip = BlockIP.query.get(id)
        if block_ip:
            # 从监控的任务队列中移除
            from utils import zlcache
            zlcache.delete(block_ip.ip)
            db.session.delete(block_ip)
            db.session.commit()
            return field.success(message='删除成功！')
        return field.params_error(message='删除失败！')


# 热搜关键字展示

class HotSearchView(views.MethodView):
    decorators = [login_required]

    def get(self):

        return render_template('admin/hot_search.html')

    def post(self):
        data = request.values
        keys = list(data.keys())
        keys.remove('page')
        keys.remove('limit')
        keyword_data = []
        page = int(request.form.get('page'))
        limit = int(request.form.get('limit'))
        start = (page - 1) * limit
        end = start + limit

        hot_search_obj = HotSearch.query
        if keys:
            if 'date_end' in keys:
                hot_search_obj = hot_search_obj.filter(HotSearch.create_time < data.get('date_end'))
            if 'date_start' in keys:
                hot_search_obj = hot_search_obj.filter(HotSearch.create_time > data.get('date_start'))
                if 'flag' in keys:
                    print(keys)
            hot_search = hot_search_obj.filter(
                and_(
                    HotSearch.visitor_id.like("%" + data.get('ID', '') + "%"),
                )).order_by(HotSearch.create_time.desc())
        else:
            hot_search = hot_search_obj.order_by(HotSearch.create_time.desc())
        # 查询的时间为大于  现在的时间-黑名单周期时间(只显示现在还在黑名单的数据)
        live_time = (datetime.datetime.now() + datetime.timedelta(
            seconds=-config.base_config.BLOCK_IP_TIMEOUT)).strftime("%Y-%m-%d %H:%M:%S")
        keywords = hot_search.slice(start, end)
        total = hot_search.count()

        for i in keywords:
            data_dict = {}
            data_dict['id'] = i.id
            data_dict['visitor_id'] = i.visitor_id
            data_dict['search'] = i.search
            data_dict['create_time'] = str(i.create_time)
            data_dict['page'] = str(i.page)
            data_dict['count'] = str(i.count)
            keyword_data.append(data_dict)

        return field.layui_success(message='查询成功！', data=keyword_data, count=total)
