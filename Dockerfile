# Use Ubuntu 20.04 which still supports SHA1-friendly OpenSSL and SSH
FROM ubuntu:20.04

# Suppress interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Python, pip, and OpenSSH client
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    openssh-client \
    curl \
    vim \
    git \
    && apt-get clean

# Install specific versions of cryptography and paramiko that support SHA1
RUN pip3 install --no-cache-dir \
    six \
    cryptography==3.4.8 \
    paramiko==2.7.2

# Copy your script into the container (adjust as needed)
COPY gpon.py /root/gpon.py

# Set working directory
WORKDIR /root

# Default command
CMD ["python3", "-u", "/root/gpon.py"]

