#!/usr/bin/env bash

##
# To be run the very first time you boot up a raspberry pi as the root user
##

set -euo pipefail


# Install docker and docker-compose
apt update && apt upgrade -y
apt install -y libffi-dev libssl-dev python3-dev python3 python3-pip
curl -sSL https://get.docker.com | sh
pip3 install docker-compose

# Configure docker
usermod -aG docker pi
systemctl enable docker

# ssh-copy-id -i ~/.ssh/id_rsa pi@raspberrypi.local