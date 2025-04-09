# syntax=docker/dockerfile:1
# Keep this syntax directive! It's used to enable Docker BuildKit

# GIROS CI/CD Demo - Dockerfile.

# The base image is Ubuntu 22.04 LTS ("jammy").
FROM ubuntu:jammy

# Some labels are defined to store metadata.
LABEL image_version="1.0.0"
LABEL app_version="1.0.0"
LABEL maintainer="David Martínez García"

# Variables to automatically install/update tzdata.
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Madrid

# Update base image with new packages.
RUN apt-get update && apt-get dist-upgrade -y && apt-get autoremove -y && apt-get autoclean

# Install some basic tools and dependencies.
RUN apt-get install -y --no-install-recommends bash python3 python3-pip openssl net-tools wget curl iputils-ping

# Install Python dependencies/requirements using PIP.
COPY ./requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Create app directory and copy the source code.
RUN mkdir -p /ci-cd-demo
COPY ./ci_cd_demo /ci-cd-demo/ci_cd_demo

# Switch to app directory as main WORKDIR.
WORKDIR /ci-cd-demo

# Finally, the ENTRYPOINT is defined.
ENTRYPOINT ["uvicorn", "ci_cd_demo.main:app", "--host", "0.0.0.0", "--port", "8080"]
