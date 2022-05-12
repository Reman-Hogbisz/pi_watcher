FROM python:3.10.4-alpine3.15

WORKDIR /usr/src/app

COPY ./requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt

COPY ./watcher.py ./

ENTRYPOINT [ "python", "./watcher.py" ]