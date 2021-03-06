import logging
from logging.handlers import RotatingFileHandler
import requests
import redis

from flask import Flask, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

from config import APP_ENV, config


db = SQLAlchemy()
mail = Mail()
redis_conn = redis.StrictRedis(host=config[APP_ENV].REDIS_HOST, port=config[APP_ENV].REDIS_PORT)


def setupLogging(level):
    '''创建日志记录'''
    # 设置日志的记录等级
    logging.basicConfig(level=level)
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    # TODO: 这里的日志记录可以根据日期命名文件名，方便查看每天的日志记录
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


# def after_request(response):
#     '''设置请求头'''
#     # response.headers.add('Access-Control-Allow-Origin', '*')
#     # if request.method == 'OPTIONS':
#     #     response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
#     #     headers = request.headers.get('Access-Control-Request-Headers')
#     #     if headers:
#     #         response.headers['Access-Control-Allow-Headers'] = headers
#     # return response
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
#     response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
#     return response


def creat_app():
    '''
    工厂函数，创建APP实例
    :return app实例
    '''
    setupLogging(config[APP_ENV].LOGGING_LEVEL)

    app = Flask(__name__)
    app.config.from_object(config[APP_ENV])

    # app = Flask(
    #     __name__,
    #     static_folder="./dist/static",
    #     template_folder="./dist"
    # )
    # @app.route('/', defaults={'path': ''})
    # @app.route('/<path:path>')
    # def catch_all(path):
    #     if app.debug:
    #         return requests.get('http://localhost:8080/{}'.format(path)).text
    #     return render_template("index.html")
    # app.config.from_object(config[APP_ENV])

    CORS(app, resources=r'/*')

    # app.after_request(after_request)

    # 创建Redis数据库连接对象

    db.init_app(app)
    mail.init_app(app)

    # 注册user 蓝图
    from app.user import api as user_api
    app.register_blueprint(user_api, url_prefix='/api/user')
    # 注册community 蓝图
    from app.community import api as community_api
    app.register_blueprint(community_api, url_prefix='/api/community')
    # 注册school 蓝图
    from app.school import api as school_api
    app.register_blueprint(school_api, url_prefix='/api/school')

    return app
