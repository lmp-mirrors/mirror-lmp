FROM python:3.11-alpine3.19

WORKDIR /src
ENTRYPOINT [ "/src/mirror-lmp.py" ]

RUN \
    apk add git && \
    pip3 install PyYAML

COPY ./ /src/