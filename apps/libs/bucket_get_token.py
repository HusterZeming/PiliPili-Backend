import json

from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest
from config import guest_Key, guest_Secret


def get_bucket_token():
    clt = client.AcsClient(guest_Key, guest_Secret, 'cn-beijing')
    # 构造"AssumeRole"请求
    request = AssumeRoleRequest.AssumeRoleRequest()
    # 指定角色
    request.set_RoleArn('acs:ram::1809987693453899:role/liuxinwang')
    # 设置会话名称，审计服务使用此名称区分调用者
    request.set_RoleSessionName('liuxinwang')
    # request.set_method('HMAC-SHA1')
    # 发起请求，并得到response
    response = clt.do_action_with_exception(request)
    credentials = (json.loads(response))['Credentials']
    json_credentials = json.dumps(credentials)
    token = (json.loads(json_credentials))['SecurityToken']
    return token