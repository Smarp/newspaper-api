FROM python:3.7.0-stretch

#Temporarily use Nuno's fork until it is merged to the main project
RUN git clone https://github.com/NunoPinheiro/newspaper.git && \
    cd newspaper && pip install -r requirements.txt

RUN pip install --no-cache-dir flask uwsgi

COPY . .
ENV NEWSPAPER_PORT 38765
EXPOSE $NEWSPAPER_PORT
CMD ["uwsgi", "--ini", "./src/wsgi.ini"]
