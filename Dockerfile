##############################################################
# Dockerfile to have a qt5.5 dev environment with qml-material
# Based on Ubuntu 15.04
##############################################################

# Set the base image
FROM ubuntu:15.04

MAINTAINER Benjamin Audren

RUN apt-get update && apt-get install -y \
   qtbase5-dev \
   git

RUN git clone https://github.com/papyros/qml-material && \
  cd qml-material && \
  qmake && make && make install
