# encoding: utf-8
import os


# 36字节的随机字符串作为密钥
SECRET_KEY = os.urandom(36)

# 开启Debug模式
DEBUG = True

# 配置数据库相关信息
DB_USERNAME = 'root'
DB_PASSWORD = '784748497'
DB_HOST = '127.0.0.1'
DB_PORT = '3306'

DB_NAME = 'pilipili'
DB_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 所有允许的访问类型
ALL_METHODS = ['GET', 'POST', 'PUT', "DELETE", "HEAD"]
