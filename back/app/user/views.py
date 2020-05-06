import base64
import re
import random

from flask import g, current_app, jsonify, request,make_response

from app import db, redis_conn
from app.user import api
from app.models import User
from app.utils.response_code import RET
from app.utils.email import send_mail


@api.route('/sigin', methods=['POST'])
def signin():
    '''用户注册接口
    :return 返回注册信息{'code': '0', 'msg': '注册成功'}
    '''
    nickname =request.json.get('Nickname')
    email =request.json.get('Email')
    password =request.json.get('Password')
    mailcode_client =request.json.get('Mailcode')
    mobile = request.json.get('Mobile')

    if not all([email, nickname, password, mailcode_client]):
        return jsonify(code=RET.PARAMERR, msg='参数不完整')

    #从Redis中获取此邮箱对应的验证码,与前端传来的数据校验
    try:
        mailcode_server = redis_conn.get('EMAILCODE:'+ email).decode()
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(code=RET.DBERR, msg='查询邮箱验证码失败')
    if mailcode_server != mailcode_client:
        current_app.logger.debug(mailcode_server)
        return jsonify(code=RET.PARAMERR, msg='邮箱验证码错误')
    user = User()
    user.email = email
    user.nickname = nickname
    user.password = password
    user.mobile = mobile
    #利用user model中的类属性方法加密用户的密码并存入数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.debug(e)
        db.session.rollback()
        return jsonify(code=RET.DBERR, msg='注册失败')
    #6.响应结果
    return jsonify(code=RET.OK, msg='注册成功')

@api.route('/login', methods=['POST'])
def login():
    '''登录
    TODO: 添加图片验证
    :return 返回响应,保持登录状态
    '''
    email = request.json.get('Email')
    password = request.json.get('Password')

    #解析Authorization
    #email, password = base64.b64decode(request.headers['Authorization'].split(' ')[-1]).decode().split(':')

    if not all([email, password]):
        return jsonify(code=RET.PARAMERR, msg='参数不完整')
    try:
        user = User.query.filter(User.email==email).first()
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(code=RET.DBERR, msg='查询用户失败')
    if not user:
        return jsonify(code=RET.NODATA, msg='用户不存在',user=user)
    if not user.verify_password(password):
        return jsonify(code=RET.PARAMERR, msg='帐户名或密码错误')

    #更新最后一次登录时间
    user.update_last_seen()
    token = user.generate_user_token()

    return jsonify(code=RET.OK, msg='登录成功',token=token)

@api.route('/mailcode', methods=['POST'])
def send_mail_code():
    '''发送邮箱验证码'''
    nickname =request.json.get('nickname')
    email =request.json.get('email')
    if not all([email, nickname]):
        return jsonify(re_code=RET.PARAMERR, msg='请填写完整的注册信息')

    #邮箱匹配正则
    #^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$
    #手机号匹配正则
    #^0\d{2,3}\d{7,8}$|^1[358]\d{9}$|^147\d{8}$

    if not re.match(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', email):
        return jsonify(RET.PARAMERR, msg='请填写正确的邮箱')

    #判断用户是否已注册
    try:
        user_email = User.query.filter(User.email == email).first()
        user_nickname = User.query.filter(User.nickname == nickname).first()
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(re_code=RET.DBERR, msg='查询数据库错误')
    #用户存在,提示该账户已被注册
    if user_email or user_nickname:
        return jsonify(re_code=RET.DATAEXIST, msg='该用户已被注册')

    #生成邮箱验证码
    email_code = '%06d' % random.randint(0,99999)
    current_app.logger.debug('邮箱验证码为: ' + email_code)
    try:
        redis_conn.set('EMAILCODE:'+ email, email_code, 1800)   #half-hour = 1800有效期
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(re_code=RET.DBERR, msg='存储邮箱验证码失败')

    #发送邮件
    send_mail(
        to = email,
        nickname = nickname,
        mailcode = email_code
    )

    return jsonify(re_code=RET.OK, msg='验证码发送成功')

