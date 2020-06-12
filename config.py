# encoding: utf-8
import os

# from flask_uploads import UploadSet, IMAGES, configure_uploads

# 36字节的随机字符串作为密钥
SECRET_KEY = os.urandom(36)

# 开启Debug模式
DEBUG = True

# 配置本地数据库相关信息，本地开发！！！修改后勿提交此文件！！！
DB_USERNAME = 'root'
DB_PASSWORD = '784748497'
DB_HOST = '127.0.0.1'
DB_PORT = '3306'

DB_NAME = 'pilipili'
DB_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

# 配置远程数据库相关信息
# DB_USERNAME = 'root'
# DB_PASSWORD = '784748497'
# DB_HOST = '127.0.0.1'
# DB_PORT = '3306'
#
# DB_NAME = 'pilipili'
# DB_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 所有允许的访问类型
ALL_METHODS = ['GET', 'POST', 'PUT', "DELETE", "HEAD"]

# app = create_app()
# app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()
# 文件上传
# images = UploadSet('images', IMAGES)
# videos = UploadSet('videos', 'mp4')
# 上传的初始化
# configure_uploads(app, [images, videos])
