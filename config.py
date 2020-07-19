# encoding: utf-8
import os
import oss2

# 36字节的随机字符串作为密钥
SECRET_KEY = "os.urandom(36)"

# 开启Debug模式
DEBUG = False

# 配置本地数据库相关信息，本地开发！！！修改后勿提交此文件！！！
DB_USERNAME = 'root'
DB_PASSWORD = '保密'
DB_HOST = '127.0.0.1'
DB_PORT = '3306'

DB_NAME = 'pilipili'
DB_URI = '保密' % (DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

# 阿里Bucket配置,此为管理员
# 保密

# 只读权限
#保密

SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 所有允许的访问类型
ALL_METHODS = ['GET', 'POST', 'PUT', "DELETE", "HEAD"]

MAX_CONTENT_LENGTH = 100*1024*1024

