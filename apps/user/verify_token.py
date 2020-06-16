from collections import namedtuple
from flask import current_app, g
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from apps.libs.error_code import AuthFailed

# 使用HTTPTokenAuth进行token验证，定义scheme为JWT
auth = HTTPTokenAuth(scheme="JWT")
# 定义namedtuple就不用在user模型中添加keys和__getitem__方法了
# 可以通过属性的方式获取uid
User = namedtuple('User', ['uid'])


@auth.verify_token
def verify(token):

    # 通过反序列化loads验证Authorization中的token是否有效
    s = Serializer(current_app.config['SECRET_KEY'])
    print("s" + s)
    try:
        print("token: "+token)
        data = s.loads(token)
        print("data: "+data)
    except BadSignature:
        raise AuthFailed(msg="token is invalid")
    except SignatureExpired:
        raise AuthFailed(msg="token is expired")
    # 反序列化出来后，获取用户id,并将用户id绑定到g.user
    uid = data['uid']
    user = User(uid)
    g.user = user
    return True
