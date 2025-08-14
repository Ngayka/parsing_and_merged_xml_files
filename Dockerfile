FROM ubuntu:latest
LABEL authors="semde"

ENTRYPOINT ["top", "-b"]