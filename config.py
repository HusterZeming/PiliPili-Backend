# encoding: utf-8
import os
import oss2

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

# 阿里Bucket配置,此为管理员
auth = oss2.Auth('LTAI4GHxSd1uqj1YWkSFJsoR', '4x5zpNNjLDPHZfTH07MyJRTtz95Kuw')
endpoint = 'https://oss-cn-beijing.aliyuncs.com'
bucket = oss2.Bucket(auth, endpoint, 'pilipili-bucket')

# 只读权限
guest_Key = 'LTAI4G2sAv9YZPY7npjXzb3W'
guest_Secret = 'RrgZoFblhs7IK7swSYJ3owviqHk3mt'

SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 所有允许的访问类型
ALL_METHODS = ['GET', 'POST', 'PUT', "DELETE", "HEAD"]

