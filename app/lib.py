import sys, logging, os
import aiofiles
from jinja2 import FileSystemLoader, Environment
from pathlib import Path
from app.config import CodeStatus, MongoConfig
from app.util import Util
from app import app


class Lib:
    ENV = app.config.name

    @classmethod
    async def Request(cls, headers=None, endpoint=None, methods=None, json=None):
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
        async with getattr(app.Session, methods)(url=endpoint, headers=headers, json=json) as response:
            sys_obj = sys._getframe()
            info = {}
            if response.content_type == 'application/json':
                content = await response.json()
            else:
                content = await response.text()
            status = response.status
            info['responseStatus'] = status
            info['requestUrl'] = str(response.url)
            info['requestMethod'] = response.method
            info['response'] = content
            return info

    @classmethod
    async def send_mail_by_msn_api(cls, subject, to, data, cc=None, bcc=None, template_path=None, feature=None):
        '''
        调用msn_api发送邮件
        :param subject:
        :param to:
        :param data:
        :param cc:
        :param bcc:
        :param template_path:
        :return:
        '''
        if cls.ENV == "Local":
            url = 'http://localhost:8085/mail/msn_cms'
        else:
            url = 'http://msnapi.eastasia.cloudapp.azure.com/mail/msn_cms'
        template_dir = Path(__file__).parent / 'templates'
        env = Environment(loader=FileSystemLoader(str(template_dir)), trim_blocks=True)
        body = env.get_template(template_path).render(data=data)
        headers = {'sender': "MMAIS-MSN"}
        res = await cls.Request(headers=headers, endpoint=url, methods='post',
                                json={"subject": subject, "body": body, "to": to, "cc": cc, "bcc": bcc,
                                      "feature": feature, "env": cls.ENV})
        response = res.get('response')
        if 'error' in response:
            logging.info('send mail {} failed'.format(to))
            message = Util.format_Resp(code_type=CodeStatus.SendMailError,
                                       message='send mail failed',
                                       exception=res['error'],
                                       sys_obj=sys._getframe()
                                       )
        else:
            logging.info('Send mail  {} successfully'.format(to))
            message = Util.format_Resp(data='Send mail successfully')
        return message

    @classmethod
    async def save_statistic_data(cls, feature='', success=0, failure=0, ignored=0):
        sum = success + failure + ignored
        if cls.ENV == "Local":
            url = 'http://localhost:8085/statistic/msn_cms'
        else:
            url = 'http://msnapi.eastasia.cloudapp.azure.com/statistic/msn_cms'

        res = await cls.Request(headers={}, endpoint=url, methods='post',
                                json={"feature": feature,
                                      "sum": sum,
                                      "success": success, "failure": failure, "ignored": ignored,
                                      "env": cls.ENV})
        if 'error' in res:
            logging.info('save statistic data failed')
            message = Util.format_Resp(code_type=CodeStatus.RequestError,
                                       message='save statistic data failed',
                                       exception=res['error'],
                                       sys_obj=sys._getframe()
                                       )
        else:
            logging.info('Save statistic data successfully')
            message = Util.format_Resp(data='Save statistic data successfully')

