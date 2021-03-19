from wtforms import StringField,    IntegerField
from wtforms.validators import DataRequired, length, Email,Length ,Regexp,InputRequired,ValidationError

from apis.common.form import BaseForm as Form

from apis.common.response_code import ParameterException


# class RegisterForm(Form):
#     email = StringField(validators=[
#         DataRequired(message='邮箱不许为空'),
#         Email(message='invalidate email')
#     ])
#     password = StringField(validators=[
#         DataRequired(message='密码不许为空'),
#         # password can only include letters , numbers and "_"
#         Regexp(r'^[A-Za-z0-9_*&$#@]{6,20}$', message='密码格式不正确')
#     ])
#     re_password = StringField(validators=[DataRequired(message='密码不许为空'), equal_to('password', message='两次密码不相同')])
#     username = StringField(validators=[DataRequired('用户名不能为空'),
#                                        length(min=2, max=20, message='用户名长度为2-20位')])
#
#     def validate_email(self, value):
#         if User.query.filter_by(email=value.data).first():
#             raise ValidationError(message='改邮箱已经被注册')
#
#     def validate_username(self, value):
#         if User.query.filter_by(username=value.data).first():
#             raise ValidationError(message='改用户名已经被使用')


class LoginForm(Form):
    username = StringField(validators=[InputRequired('请输入邮箱或者用户名')])
    password = StringField(validators=[Length(6, 20, message='请输入正确格式的密码'), InputRequired(message='请输入密码')])
    vercode = StringField(validators=[Regexp(r'\w{4}', message='请输入正确格式的图形验证码！'), InputRequired(message='请输入验证码')])

    def validate_vercode(self, field):
        from utils import zlcache
        graph_captcha = field.data
        graph_captcha_mem = zlcache.get(graph_captcha.lower())
        if not graph_captcha_mem:
            raise ParameterException(message='图形验证码错误!')
            # raise ValidationError(message='图形验证码错误！')
        else:
            zlcache.delete(graph_captcha.lower())




class UserinfoForm(Form):
    note = StringField(validators=[
        length(min=0, max=254, message='备注最多为255个字符')])
    # email = StringField(validators=[
    #     DataRequired(message='邮箱不许为空'),
    #     Email(message='invalidate email')
    # ])
