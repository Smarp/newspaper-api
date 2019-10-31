FROM python:3.8-alpine

RUN apk add gcc git

#for pillow
RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev

#for lxml
RUN apk add --update --no-cache --virtual .build-deps \
        g++ \
        python-dev \
        libxml2 \
        libxml2-dev && \
    apk add libxslt-dev && \
    apk del .build-deps

# for uwsgi
RUN apk add build-base linux-headers

RUN pip3 install --no-cache-dir flask html.parser uwsgi

#Clone newspaper project and checkout specific commit
RUN git clone https://github.com/codelucas/newspaper.git && \
    cd newspaper && git checkout 11cbf3a3038c0630d14e55743b942b6f36624a6b \
    && pip3 install -r requirements.txt

COPY . .
ENV NEWSPAPER_PORT 38765
EXPOSE $NEWSPAPER_PORT
CMD ["uwsgi", "--ini", "./src/wsgi.ini"]

