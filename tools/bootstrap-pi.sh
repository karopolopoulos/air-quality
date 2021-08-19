#!/usr/bin/env bash

##
# To be run the very first time you boot up a raspberry pi as the root user
##

set -euo pipefail


# Install docker and docker-compose
apt update && apt upgrade -y
apt install -y libffi-dev libssl-dev python3-dev python3 python3-pip
wget http://ftp.us.debian.org/debian/pool/main/libs/libseccomp/libseccomp2_2.5.1-1_armhf.deb
dpkg -i libseccomp2_2.5.1-1_armhf.deb
curl -sSL https://get.docker.com | sh
pip3 install docker-compose

# Configure docker
usermod -aG docker pi
systemctl enable docker

# ssh-copy-id -i ~/.ssh/id_rsa pi@raspberrypi.local
# echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="SDS011"' >> /etc/udev/rules.d/99_usbdevices.rules