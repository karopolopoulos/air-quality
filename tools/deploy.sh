#!/usr/bin/env bash

set -euo pipefail

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
build_dir=${__dir}/../build
src_dir=${__dir}/..
project_name=air-quality

prepare() {
  echo "Cleaning up build directory..."

  if [[ -d $build_dir ]]; then 
    rm -rf "${build_dir}"
  fi

  mkdir -p "${build_dir}/${project_name}"
}

package() {
  echo "Packaging required files..."

  cp -r "${src_dir}/docker-compose.yml" "${src_dir}/.env" "${src_dir}/certs" "${build_dir}/${project_name}/"

  cd "${build_dir}"
  zip -r "${project_name}.zip" "${project_name}"
}

transfer_and_download() {
  echo "Transferring package to raspberry pi..."
  scp "${build_dir}/${project_name}.zip" pi@raspberrypi.local:/home/pi/

  echo "Downloading air-quality image to raspberry pi..."
  ssh pi@raspberrypi.local "unzip -o ${project_name}.zip \
    && cd ${project_name} \
    && docker-compose pull"
}

start() {
  echo "Starting service on raspberry pi..."
  ssh pi@raspberrypi.local "cd ${project_name} \
    && docker-compose up"
}

run() {
  prepare
  package
  transfer_and_download
  start
}

run