#Monitor-Probe
#
#VERSION 1.0

FROM python:3.7
LABEL AUTHOR="Niu Ben<v-beniu@microsoft.com>"
USER root

WORKDIR /usr/src/tomato
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get update && apt-get install -y wget vim
COPY requirements.txt ./
RUN pip install --no-cache-dir -i https://pypi.douban.com/simple -r requirements.txt
COPY . .

CMD ["python", "main.py"]