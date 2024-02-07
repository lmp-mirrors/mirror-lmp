FROM python:3.11-alpine3.19

WORKDIR /src
ENTRYPOINT [ "/src/mirror-lmp.py" ]

RUN \
    apk add git openssh-client && \
    pip3 install PyYAML

COPY mirror-lmp.py /src/
COPY lmp-mirrors.yaml /src/
COPY known_hosts /root/.ssh/known_hosts
