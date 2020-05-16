import sys, re, logging, time
import jwt
from datetime import datetime, timedelta
from app.config import CodeStatus
from datetime import datetime
from uuid import uuid4


class Util:
    @classmethod
    def format_Resp(cls, code_type=CodeStatus.SuccessCode,
                    errorDetail='',
                    data='',
                    message='',
                    sys_obj=sys._getframe(),
                    exp_obj=None,
                    **kwargs
                    ):
        '''
        定义返回Response模板
        :param code_type:   int|错误状态
        :param errorDetail: str|错误详情
        :param data:   str|request成功后填充
        :param alert: str|前端显示信息
        :param message:  str|提示信息
        :param sys_obj:  Obj|获取当前文件名,函数名,所在行数
        :return:
        '''
        Resp = {}
        Resp['code'] = code_type.value

        if errorDetail:
            Resp['errorDetail'] = {"file": sys_obj.f_code.co_filename.split('/')[-1],
                                   "function": sys_obj.f_code.co_name,
                                   "lineNo": sys_obj.f_lineno,
                                   'exception': errorDetail
                                   }
        elif exp_obj:
            Resp['errorDetail'] = cls.exception_handler(exp_obj)
        else:
            Resp['data'] = data

        if Resp.get('errorDetail'):
            exception = Resp['errorDetail'].get('exception')
            Resp['message'] = message if message else exception
        else:
            Resp['message'] = message if message else code_type.name
        if kwargs:
            for key, value in kwargs.items():
                Resp[str(key)] = value
        return Resp

    @classmethod
    def exception_handler(cls, exp_obj):
        tb_next = exp_obj[2].tb_next
        exception = exp_obj[0].__name__ + ":" + str(exp_obj[1]).replace("'", '')
        import traceback
        if not tb_next:

            tb_frame = exp_obj[2].tb_frame
            last_stack = traceback.extract_stack(tb_frame)[-1]
            lineno = last_stack.lineno
            filename = last_stack.filename.split('/')[-1]
            func_name = last_stack.name
        else:
            while tb_next:
                if not tb_next.tb_next:
                    break
                else:
                    tb_next = tb_next.tb_next
            tb_frame = tb_next.tb_frame
            filename = tb_frame.f_code.co_filename
            func_name = tb_frame.f_code.co_name
            lineno = tb_frame.f_lineno

        return {"file": filename, "function": func_name,
                "lineNo": lineno, "exception": exception
                }

    @classmethod
    def key_validate(cls, data, node_name):
        '''
        针对A.B.C　的字符串类型进行递归判断,如果不存在相应字段,返回相应错误
        :param data:
        :type data: dict
        :param node_name:
        :type node_name: str
        :return:
        :rtype:
        '''
        key_list = node_name.split('.')
        if not isinstance(data, dict):
            return cls.format_Resp(code_type=CodeStatus.InvalidDataError, message='parameter data must be dict')
        try:
            for index, key in enumerate(key_list):
                match_res = re.findall(r'(.*)\[(.+?)\]', key)
                if match_res:
                    k1, index1 = match_res[0][0], match_res[0][1]
                    if not k1:
                        return cls.format_Resp(code_type=CodeStatus.ParametersMissError,
                                               message="{} doesn't exists".format(k1))

                    data = data[k1][int(index1)]
                else:
                    data = data[key]
            return cls.format_Resp(data=data)
        except:
            exp = sys.exc_info()
            return Util.format_Resp(code_type=CodeStatus.UnknownError, exp_obj=exp)

    @classmethod
    def get_now_time(cls):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def get_utc_time(cls):
        return datetime.utcnow()

    @classmethod
    def gen_id(cls):
        return str(uuid4())[:7]


class Auth():
    @staticmethod
    async def encode_auth_token(user_name):
        """
        生成认证Token
        :param user_id: int
        :param login_time: int(timestamp)
        :return: string
        """
        from app import app
        config = await app.config.config
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(seconds=config.get("tokenExpired", 3600)),
                'iss': 'myvue',
                'iat': datetime.utcnow(),
                'data': {
                    'username': user_name,
                    'login_time': Util.get_now_time()
                }
            }
            return Util.format_Resp(data=jwt.encode(
                payload,
                'secret',
                algorithm='HS256'
            ).decode('utf-8'))
        except:
            exp = sys.exc_info()
            return Util.format_Resp(code_type=CodeStatus.UnknownError, message="encode token failed",
                                    sys_obj=sys._getframe(), exp_obj=exp)

    @staticmethod
    def decode_auth_token(auth_token):
        """
        验证Token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, 'secret')
            if ('data' in payload and 'username' in payload['data']):
                return Util.format_Resp(data=payload)
            else:
                raise jwt.InvalidTokenError

        except jwt.ExpiredSignatureError:
            return Util.format_Resp(code_type=CodeStatus.Unauthorized, message="token is expired")
        except jwt.InvalidTokenError:
            return Util.format_Resp(code_type=CodeStatus.Unauthorized, message="token is invalid")

    # def identify(self, request):
    #     """
    #     用户鉴权
    #     :return: list
    #     """
    #     auth_header = request.headers.get('Authorization')
    #     if (auth_header):
    #         auth_tokenArr = auth_header.split(" ")
    #         if (not auth_tokenArr or auth_tokenArr[0]!= 'jwt' or len(auth_tokenArr) != 2 ):
    #             result = common.falseReturn('','请传递正确的验证头信息')
    #         else:
    #             auth_token = auth_tokenArr[1]
    #             payload = self.decode_auth_token(auth_token)
    #             if not isinstance(payload, str):
    #                 userDao = UserDao()
    #                 user = userDao.search(payload['data']['id'])
    #                 if (user is None):
    #                     result = common.falseReturn('', '找不到该用户信息')
    #                 else:
    #                     result = common.trueReturn('', '请求成功')
    #             else:
    #                 result = common.falseReturn('', payload)
    #     else:
    #         result = common.falseReturn('','没有提供认证token')
    #     return result
