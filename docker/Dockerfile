# Build these with the build.py script
# Example:
#   python3 docker/build.py --tag dev --arch amd64 --build-type docker build

# One of "docker", "hassio"
ARG BASEIMGTYPE=docker

# https://github.com/hassio-addons/addon-debian-base/releases
FROM ghcr.io/hassio-addons/debian-base:6.2.3 AS base-hassio
# https://hub.docker.com/_/debian?tab=tags&page=1&name=bullseye
FROM debian:bullseye-20230208-slim AS base-docker

FROM base-${BASEIMGTYPE} AS base

ARG TARGETARCH
ARG TARGETVARIANT

RUN \
    apt-get update \
    # Use pinned versions so that we get updates with build caching
    && apt-get install -y --no-install-recommends \
        python3=3.9.2-3 \
        python3-pip=20.3.4-4+deb11u1 \
        python3-setuptools=52.0.0-4 \
        python3-pil=8.1.2+dfsg-0.3+deb11u1 \
        python3-cryptography=3.3.2-1 \
        python3-venv=3.9.2-3 \
        iputils-ping=3:20210202-1 \
        git=1:2.30.2-1+deb11u2 \
        curl=7.74.0-1.3+deb11u7 \
        openssh-client=1:8.4p1-5+deb11u1 \
    && rm -rf \
        /tmp/* \
        /var/{cache,log}/* \
        /var/lib/apt/lists/*

ENV \
  # Fix click python3 lang warning https://click.palletsprojects.com/en/7.x/python3/
  LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN \
    # Ubuntu python3-pip is missing wheel
    pip3 install --no-cache-dir \
        wheel==0.37.1


# First install requirements to leverage caching when requirements don't change
COPY requirements.txt /
RUN \
    pip3 install --no-cache-dir -r /requirements.txt


# ======================= docker-type image =======================
FROM base AS docker

# Copy webserver and install
COPY . /webserver
RUN pip3 install --no-cache-dir --no-use-pep517 -e /webserver

# Settings for webserver
ENV USERNAME="" PASSWORD=""

# Expose the webserver to Docker
EXPOSE 8888

COPY docker/docker_entrypoint.sh /entrypoint.sh
RUN ["chmod", "+x", "/entrypoint.sh"]
# The directory the user should mount their configuration files to
VOLUME /config
WORKDIR /webserver
# Set entrypoint to webserver (via a script) so that the user doesn't have to type 'webserver'
# in every docker command twice
ENTRYPOINT ["/entrypoint.sh"]
# When no arguments given, start the webserver in the workdir
CMD ["webserver"]


# ======================= hassio-type image =======================
FROM base AS hassio

RUN \
    apt-get update \
    # Use pinned versions so that we get updates with build caching
    && apt-get install -y --no-install-recommends \
        nginx-light=1.18.0-6.1+deb11u3 \
    && rm -rf \
        /tmp/* \
        /var/{cache,log}/* \
        /var/lib/apt/lists/*

ARG BUILD_VERSION=dev

# Copy root filesystem
COPY docker/ha-addon-rootfs/ /

# Copy webserver and install
COPY . /webserver
RUN pip3 install --no-cache-dir --no-use-pep517 -e /webserver

# Labels
LABEL \
    io.hass.name="WebServer" \
    io.hass.description="Simple Webserver based on tornado" \
    io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}"
    # io.hass.arch is inherited from addon-debian-base

