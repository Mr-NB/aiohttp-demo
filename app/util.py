import sys, re, logging
from app.config import CodeStatus
from datetime import datetime


class Util:
    @classmethod
    def format_Resp(cls, code_type=CodeStatus.SuccessCode,
                    data='',
                    message='',
                    sys_obj=None,
                    exp_obj=None,
                    exception='',
                    **kwargs
                    ):
        '''
        定义返回Response模板
        :param code_type:   int|错误状态
        :param errorDetail: str|错误详情
        :param data:   str|request成功后填充
        :param message:  str|提示信息
        :param sys_obj:  Obj|获取当前文件名,函数名,所在行数
        :return:
        '''
        Resp = {}
        Resp['code'] = code_type.value

        if sys_obj:
            Resp['errorDetail'] = {"file": sys_obj.f_code.co_filename.split('/')[-1],
                                   "function": sys_obj.f_code.co_name,
                                   "lineNo": sys_obj.f_lineno,
                                   "exception": exception
                                   }
        elif exp_obj:
            exception = cls.exception_handler(exp_obj)
            Resp['errorDetail'] = exception
            message = exception.get('exception')
        else:
            Resp['data'] = data
        Resp['message'] = message if message else code_type.name
        if kwargs:
            for key, value in kwargs.items():
                Resp[str(key)] = value
        return Resp

    @classmethod
    def exception_handler(clsm, exp_obj):
        tb_next = exp_obj[2].tb_next
        while tb_next:
            if not tb_next.tb_next:
                break
            else:
                tb_next = tb_next.tb_next
        tb_frame = tb_next.tb_frame
        filename = tb_frame.f_code.co_filename
        func_name = tb_frame.f_code.co_name
        lineno = tb_frame.f_lineno
        exception = exp_obj[0].__name__ + ":" + str(exp_obj[1]).replace("'", '')
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
            return Util.format_Resp(code_type=CodeStatus.UnknownError, exc_obj=exp)

    @classmethod
    def get_now_time(cls):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def get_utc_time(cls):
        return datetime.utcnow()
