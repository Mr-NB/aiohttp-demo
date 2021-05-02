import os
import sys, time, json

from app.util import Util

import asyncoss
import oss2
from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest


class Lib:
    # ENV = app.config.name

    @classmethod
    async def Request(cls, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"},
                      endpoint=None, methods="get", json=None, token=None):
        '''

        :param headers:
        :type headers: dict
        :param endpoint:
        :type endpoint: str
        :param methods: get/post/put/delete
        :type methods: str
        :param json:
        :type json: dict
        :return:
        :rtype:
        '''
        from app import app
        if token:
            headers['Authorization'] = token
        async with getattr(app.Session, methods)(url=endpoint, headers=headers, json=json) as response:
            sys_obj = sys._getframe()
            info = {}
            if response.content_type == 'application/json':
                content = await response.json()
            elif "image" in response.content_type:
                content = await response.content.read()
            else:
                content = await response.text()
            status = response.status
            info['responseStatus'] = status
            info['requestUrl'] = str(response.url)
            info['requestMethod'] = response.method
            info['content_type'] = response.content_type
            info['response'] = content
            return info

    @classmethod
    async def save_file(cls, data, request):
        path = await OSS.upload(data.get("file"), data.get("type"), request)
        # abspath 缩略图 origin 原图
        return {"path": path, "absPath": cls.get_abs_path("{}?x-oss-process=image/resize,p_50".format(path)),
                "originPath": cls.get_abs_path(path)}

    @classmethod
    def get_abs_path(cls, path):
        return "{}/{}".format(
            os.getenv("STATICFILEDOMAIN", "https://agro-cloud-doctor-pictures.oss-cn-beijing.aliyuncs.com"), path)


class OSS:
    endpoint = 'http://oss-cn-beijing.aliyuncs.com'
    auth = asyncoss.Auth('LTAI4G6tKEtDrgfKK3hrvFoe', 'Wl4rzn8nBhGMbSDcbPgeJSj3xuf5mc')
    bucketName = 'agro-cloud-doctor-pictures'

    @classmethod
    async def upload(cls, fileObj=None, path=None, request=None, content=None):
        '''

        :param fileObj:
        :param path:
        :param request: 获取customerId、stationId
        :param content: file stream
        :return:
        '''
        async with asyncoss.Bucket(cls.auth, cls.endpoint, cls.bucketName) as bucket:
            basePath = "{}/{}/{}".format(Util.get_now("%Y%m%d"), request.customerId,
                                         request.id)
            if content:
                fullFileName = "{}/{}".format(
                    basePath, path)
            else:
                suffix = fileObj.filename.split(".")[-1]
                fileName = Util.gen_md5_hash("{}+{}".format(fileObj.filename, time.time()))
                fullFileName = "{}/{}/{}.{}".format(
                    basePath, path, fileName, suffix)
                content = fileObj.file.read()
            await bucket.put_object(fullFileName, content)
            return fullFileName

    @classmethod
    async def download(cls, fileName):
        async with asyncoss.Bucket(cls.auth, cls.endpoint, cls.bucketName) as bucket:
            result = await bucket.get_object(fileName)
            await result.resp.read()

    @classmethod
    async def delete(cls, fileName):
        async with asyncoss.Bucket(cls.auth, cls.endpoint, cls.bucketName) as bucket:
            await bucket.delete_object(fileName)
            return Util.format_Resp(message="delete successfully")

    @classmethod
    def get_temp_url(cls, objName):
        bucket = oss2.Bucket(cls.auth, cls.endpoint, cls.bucketName)
        return bucket.sign_url('GET', objName, int(os.getenv("STATIC_FILE_EXPIRED_TIME", 600)))


access_key_id = os.getenv('OSS_TEST_STS_ID', 'LTAI4G6tKEtDrgfKK3hrvFoe')
access_key_secret = os.getenv('OSS_TEST_STS_KEY', 'Wl4rzn8nBhGMbSDcbPgeJSj3xuf5mc')
bucket_name = os.getenv('OSS_TEST_BUCKET', 'agro-cloud-doctor-pictures')
endpoint = os.getenv('OSS_TEST_ENDPOINT', 'http://oss-cn-beijing.aliyuncs.com')
sts_role_arn = os.getenv('OSS_TEST_STS_ARN', 'oss-access@31661121.onaliyun.com')


class StsToken(object):
    """AssumeRole返回的临时用户密钥
    :param str access_key_id: 临时用户的access key id
    :param str access_key_secret: 临时用户的access key secret
    :param int expiration: 过期时间，UNIX时间，自1970年1月1日UTC零点的秒数
    :param str security_token: 临时用户Token
    :param str request_id: 请求ID
    """

    def __init__(self):
        self.access_key_id = ''
        self.access_key_secret = ''
        self.expiration = 0
        self.security_token = ''
        self.request_id = ''

    def fetch_sts_token(access_key_id, access_key_secret, role_arn):
        """子用户角色扮演获取临时用户的密钥
        :param access_key_id: 子用户的 access key id
        :param access_key_secret: 子用户的 access key secret
        :param role_arn: STS角色的Arn
        :return StsToken: 临时用户密钥
        """
        clt = client.AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')
        req = AssumeRoleRequest.AssumeRoleRequest()

        req.set_accept_format('json')
        req.set_RoleArn(role_arn)
        req.set_RoleSessionName('oss-python-sdk-example')

        body = clt.do_action_with_exception(req)

        j = json.loads(oss2.to_unicode(body))

        token = StsToken()

        token.access_key_id = j['Credentials']['AccessKeyId']
        token.access_key_secret = j['Credentials']['AccessKeySecret']
        token.security_token = j['Credentials']['SecurityToken']
        token.request_id = j['RequestId']
        token.expiration = oss2.utils.to_unixtime(j['Credentials']['Expiration'], '%Y-%m-%dT%H:%M:%SZ')

        return token


# # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
# token = StsToken.fetch_sts_token(access_key_id, access_key_secret, sts_role_arn)
# auth = oss2.StsAuth(token.access_key_id, token.access_key_secret, token.security_token)
# bucket = oss2.Bucket(auth, endpoint, bucket_name)
#
#
# # 上传一段字符串。Object名是motto.txt，内容是一段名言。
# bucket.put_object('motto.txt', 'Never give up. - Jack Ma')
import asyncio

# print(OSS.get_temp_url("20201231/customerId/stationId/work/d9e773f6e3f416a592ca4524059975c4.png"))
