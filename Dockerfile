FROM ubuntu:24.04

# Disable interactive prompts during build
ARG DEBIAN_FRONTEND=noninteractive

# --- System update and basic setup ---
# Update package lists and install essential build tools and utilities.
RUN apt-get -o APT::Retries=3 update -y && \
    apt-get -o APT::Retries=3 install -y --no-install-recommends \
    bash \
    bc \
    binutils \
    build-essential \
    bzip2 \
    bzr \
    ca-certificates \
    cmake \
    cpio \
    curl \
    cvs \
    diffutils \
    file \
    findutils \
    gawk \
    g++ \
    g++-multilib \
    gcc \
    gcc-multilib \
    git \
    graphviz \
    gzip \
    libgnutls28-dev \
    libncurses-dev \
    libssl-dev \
    locales \
    make \
    patch \
    perl \
    python3-matplotlib \
    rsync \
    sed \
    tar \
    unzip \
    wget \
    which && \
    # Remove unnecessary packages to minimize image size
    apt-get remove -y '*cloud*' '*firefox*' '*chrome*' '*dotnet*' '*php*' && \
    apt-get -y autoremove && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/*

# --- Locale configuration ---
# Enable the UTF-8 locale for proper encoding support during builds.
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV TZ=Europe/Paris

# --- Create non-root build user ---
# Improves security by avoiding root operations during compilation.
RUN useradd -m -s /bin/bash build && \
    mkdir -p /build && \
    chown build:build /build

# Set the working directory and switch to the build user
WORKDIR /build
USER build

# --- Default command ---
# Start a Bash shell when the container runs.
CMD ["/bin/bash"]
