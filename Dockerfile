FROM ubuntu:latest
LABEL authors="dedyvka"

ENTRYPOINT ["top", "-b"]