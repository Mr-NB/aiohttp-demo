#xigua video url prase
#
#VERSION 1.0.0

FROM python:3.7
LABEL AUTHOR="Niu Ben<v-beniu@microsoft.com>"
USER root

WORKDIR /usr/src/xigua
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean
RUN apt-get clean && apt-get update && apt-get install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget vim

COPY requirements.txt ./
RUN pip install --no-cache-dir -i https://pypi.douban.com/simple -r requirements.txt
COPY . .

CMD ["python", "main.py"]