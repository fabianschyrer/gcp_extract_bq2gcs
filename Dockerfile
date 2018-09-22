FROM python:3.6-alpine
WORKDIR /usr/src/app

RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pyb -v

RUN cp -R /usr/src/app/target/dist/app-1.0.dev0/. /usr/src/dist/
RUN cp -R /usr/src/app/target/reports/. /usr/src/reports/
RUN rm -rf /usr/src/app
RUN cp -R /usr/src/dist/. /usr/src/app/
RUN rm -rf /usr/src/dist

COPY entrypoint.sh .
RUN chmod 755 entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
