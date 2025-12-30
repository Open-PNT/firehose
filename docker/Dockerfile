FROM ubuntu:22.04

# Necessary to avoid prompts to configure timezone data.
ENV DEBIAN_FRONTEND noninteractive

# Install common dependencies
# apt-transport-https: For using HTTPS to communicate with APT repositories
# bash-completion: For tab completion while using git, etc.
# build-essential: For compiling ASPN-C, etc.
# ca-certificates: To allow HTTPS connections
# clang-format: For formatting source code
# cmake: For building the LCM subproject
# default-jdk: For Java development
# git: For development
# gnupg: For package verification
# gradle: For building LCM jar
# libasio-dev: For developing applications using ASIO
# libglib2.0-dev: To build LCM
# liblcm-dev: For LCM (Lightweight Communications and Marshalling) library
# libpython3-dev: For building python modules via pybind
# libtinyxml2-dev: For XML parsing
# meson: For building source code projects
# ninja-build: For building source code projects
# openssh-server: for using git over ssh
# python-is-python3: To start python3 with the `python` command
# python3-numpy: For xtensor-python
# python3-pip: For installing pip packages
# python3.10-venv: For building Python packages
# software-properties-common: To manage repositories
# ssh: For using git over ssh
# vim: For file editing, git commits
# wget: For retrieving files via HTTP, HTTPS, and FTP
RUN apt-get update && apt-get install -y --no-install-recommends \
  apt-transport-https \
  bash-completion \
  build-essential \
  ca-certificates \
  clang-format \
  cmake \
  default-jdk \
  git \
  gnupg \
  gradle \
  libasio-dev \
  libglib2.0-dev \
  libpython3-dev \
  libtinyxml2-dev \
  meson \
  ninja-build \
  openjdk-8-jdk \
  python-is-python3 \
  python3-numpy \
  python3-pip \
  python3.10-venv \
  software-properties-common \
  ssh \
  vim \
  wget \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Set up work directory
WORKDIR /opt/fastdds_docker_ws

# Clone and build Fast-DDS dependency foonathan_memory_vendor
RUN git clone https://github.com/eProsima/foonathan_memory_vendor.git src/foonathan_memory_vendor \
  && cd src/foonathan_memory_vendor \
  && git checkout v1.3.1 \
  && mkdir build \
  && cd build \
  && cmake .. \
  && cmake --build . --target install -- -j$(nproc) \
  && ldconfig

# Clone and setup Fast-CDR
RUN git clone https://github.com/eProsima/Fast-CDR.git src/Fast-CDR \
  && cd src/Fast-CDR \
  && git checkout v2.2.0 \
  && mkdir build \
  && cd build \
  && cmake .. \
  && cmake --build . --target install -- -j$(nproc) \
  && ldconfig

# Clone and setup Fast-DDS
RUN git clone https://github.com/eProsima/Fast-DDS.git src/Fast-DDS \
  && cd src/Fast-DDS \
  && git checkout v2.14.0 \
  && mkdir build \
  && cd build \
  && cmake .. \
  && cmake --build . --target install -- -j$(nproc) \
  && ldconfig

# Clone and setup Fast-DDS-Gen
RUN git clone https://github.com/eProsima/Fast-DDS-Gen.git src/Fast-DDS-Gen \
  && cd src/Fast-DDS-Gen \
  && git checkout v3.3.0 \
  && ./gradlew assemble \
  && ./gradlew install --install_path=/usr/local/

# Install Python packages
RUN pip3 install black pyyaml isort

WORKDIR /firehose

# Necessary to encode certain characters when compiling the Java code.
ENV LANG=C.UTF-8

COPY user_bootstrap.sh /
ENTRYPOINT ["/user_bootstrap.sh"]
