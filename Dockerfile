FROM checksum/python-newspaper:latest

RUN pip install --no-cache-dir flask


COPY . .
ENV NEWSPAPER_PORT 38765
EXPOSE $NEWSPAPER_PORT

CMD ["python", "./src/server.py"]
