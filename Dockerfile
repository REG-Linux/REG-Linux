FROM ubuntu:24.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    cmake \
    git \
    libncurses6 \
    libncurses-dev \
    libssl-dev \
    mercurial \
    texinfo \
    zip \
    default-jre \
    imagemagick \
    subversion \
    autoconf \
    automake \
    bison \
    scons \
    libglib2.0-dev \
    bc \
    mtools \
    u-boot-tools \
    flex \
    wget \
    cpio \
    dosfstools \
    libtool \
    rsync \
    device-tree-compiler \
    gettext \
    locales \
    graphviz \
    python3 \
    python3-numpy \
    python3-matplotlib \
    gcc-multilib \
    g++-multilib \
    libgnutls28-dev \
    fonts-droid-fallback \
    libcurl4-openssl-dev \
    rapidjson-dev \
    libasound2-dev \
    libcec-dev \
    libboost-all-dev \
    libint-dev \
    libavcodec-dev \
    libfreetype6-dev \
    libsdl2-dev \
    libsdl2-mixer-dev \
    libfreeimage-dev \
    libavfilter-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV TZ Europe/Paris

# Workaround host-tar configure error
ENV FORCE_UNSAFE_CONFIGURE 1

RUN mkdir -p /build
WORKDIR /build

CMD ["/bin/bash"]
