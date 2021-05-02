FROM python:3.7
LABEL AUTHOR="Niu Ben<iamfuture_x@outlook.com>"
USER root

WORKDIR /usr/src/app
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean

COPY requirements.txt ./
RUN pip install --no-cache-dir -i https://pypi.douban.com/simple -r requirements.txt
COPY . .
#ENTRYPOINT aerich init -t app.models.TORTOISE_ORM && aerich init-db && aerich migrate && aerich upgrade && python main.py
CMD ["python","main.py"]

