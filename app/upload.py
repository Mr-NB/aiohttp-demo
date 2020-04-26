import xlrd, sys
from pathlib import Path
from app import app
from app.util import Util
from app.config import CodeStatus
from app.db import MONGO
import aiofiles


class BaseUpload:

    def __init__(self, uploaded_file=None, username=None):

        self.uploaded_file = uploaded_file
        self.commitId = Util.gen_id()
        self.username = username
        self.fileType = ""

        self.parentPath = str(Path(__file__).parent)

    async def filter(self, content, *args, **kwargs):
        if self.fileType:
            return await getattr(self, "{}_filter".format(self.fileType))(content)
        return Util.format_Resp(code_type=CodeStatus.FormatError, message='Invalid file')

    async def main(self):

        # Gets file.
        file = self.uploaded_file.file
        if not file:
            return Util.format_Resp(code_type=CodeStatus.NotFoundError, errorDetail='No uploaded file')
        config = await app.config.config
        try:
            fileSuffix = self.uploaded_file.filename.split(".")[-1]
            if fileSuffix in config.get("allowExcelType", ["xls", "xlsx"]):
                self.fileType = "excel"
            elif fileSuffix in config.get("allowImageType", ["png", "jpg"]):
                self.fileType = "image"
            else:
                self.fileType = ""
        except:
            self.fileType = ""

        # Gets content.
        content = file.read()
        if not content:
            return Util.format_Resp(code_type=CodeStatus.NotFoundError, errorDetail='No content in file')
        return await self.filter(content)

    async def excel_filter(self, content):
        '''
        basic excel fiter condition
        :param content:
        :type content:
        :param ExcelMandatoryFields: must be fill
        :type ExcelMandatoryFields: list
        :return:
        :rtype:
        '''
        # Reads content.
        excel_workbook = xlrd.open_workbook(file_contents=content)
        tables = excel_workbook.sheets()
        all_data = []
        for table in tables:
            table_name = str(table.name).strip()
            data_rows = table._cell_values
            if len(data_rows) <= 1:
                return Util.format_Resp(code_type=CodeStatus.NoDataError, message='Sheet:{} no data'.format(table_name))
            else:
                item_list = []
                # remove spaces before and after str
                for oItem in data_rows:
                    for soIndex, soItem in enumerate(oItem):
                        if isinstance(soItem, str):
                            oItem[soIndex] = soItem.strip().replace("，", ',').replace("：", ":")
                        if isinstance(soItem, float):
                            oItem[soIndex] = str(int(soItem))

                    item_list.append(oItem)
                all_data.append({'data': item_list, "table_name": table_name})

        return Util.format_Resp(data=all_data)

    async def image_filter(self, content):
        '''
        basic image filter condition
        :param content:
        :return:
        '''
        return Util.format_Resp(data=content)

    async def upload(self, params):

        uploadFile = params.get("file")
        commitId = params.get("commitId")
        if commitId:
            self.commitId = commitId
        findRes = await MONGO(collectionName=self.uploadCollection).find({"commitId": self.commitId}, length=1)
        if not findRes:
            name = params.get("name", Util.get_now_time())
            updateData = {
                "updateDate": Util.get_now_time(),
                "commitId": self.commitId

            }
        else:
            data = findRes[0]
            name = data.get("name")
            updateData = data

        filePath = "/static/images/{}/{}.png".format(self.name, name)
        if uploadFile:
            self.uploaded_file = uploadFile
            contentRes = await self.main()
            if contentRes.get("code") != 200:
                return contentRes
            content = contentRes.get("data")

            async with aiofiles.open(self.parentPath + filePath, mode='wb') as f:
                await f.write(content)

            updateData['filePath'] = filePath

        updateData.update(params)
        if updateData.get("file"):
            del updateData['file']
        await MONGO(collectionName=self.uploadCollection).update_one({"commitId": self.commitId}, {"$set": updateData})
        return Util.format_Resp(data="upload successfully")
