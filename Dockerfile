##############################################################
# Dockerfile to have a qt5.5 dev environment with qml-material
# Based on Ubuntu 15.04
##############################################################

# Set the base image
FROM ubuntu:trusty

MAINTAINER Benjamin Audren
 
LABEL description="Running Qml NoteOrganiser" 

RUN apt-get update && apt-get install -y \
  software-properties-common \
  python-software-properties &&\
  add-apt-repository ppa:beineri/opt-qt55-trusty
RUN apt-get update && apt-get install -y \
  git \
  qt55-meta-full \
  build-essential \
  mesa-common-dev \
  libglu1-mesa-dev && rm -rf /var/lib/apt/lists/*

ENV QT_BASE_DIR=/opt/qt55
ENV QTDIR=$QT_BASE_DIR
ENV PATH=$QT_BASE_DIR/bin:$PATH
ENV LD_LIBRARY_PATH=$QT_BASE_DIR/lib/x86_64-linux-gnu:$QT_BASE_DIR/lib:$LD_LIBRARY_PATH
ENV PKG_CONFIG_PATH=$QT_BASE_DIR/lib/pkgconfig:$PKG_CONFIG_PATH

WORKDIR /usr/src

RUN git clone https://github.com/papyros/qml-material.git
RUN cd qml-material && qmake && make && make install && cd ..

RUN mkdir noteorganiser
COPY noteorganiser/ /usr/src/noteorganiser

RUN /bin/bash
