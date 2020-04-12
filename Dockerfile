#xigua video url prase
#
#VERSION 1.0.0

FROM python:3.7
LABEL AUTHOR="Niu Ben<v-beniu@microsoft.com>"
USER root

WORKDIR /usr/src/xigua
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean

COPY requirements.txt ./
RUN pip install --no-cache-dir -i https://pypi.douban.com/simple -r requirements.txt
COPY . .

CMD ["python", "main.py"]