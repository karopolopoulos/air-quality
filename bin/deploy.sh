#!/usr/bin/env bash

set -e
set -u
set -o pipefail

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
buildDir=${__dir}/../build
srcDir=${__dir}/..
projectName=air-quality

prepare() {
  echo "Cleaning up build directory..."

  if [[ -d $buildDir ]]; then 
    rm -rf "${buildDir}"
  fi

  mkdir -p "${buildDir}/${projectName}"
}

package() {
  echo "Packaging application..."

  cp -R "${srcDir}/requirements.txt" "${srcDir}/.env" "${srcDir}/certs" "${srcDir}/lib" "${buildDir}/${projectName}/"

  cd "${buildDir}"
  zip -r "${projectName}.zip" "${projectName}"
}

build_and_deploy() {
  echo "Uploading package to raspberry pi..."
  scp "${buildDir}/${projectName}.zip" pi@raspberrypi.local:/home/pi/

  echo "Building and deploying on raspberry pi..."
  ssh pi@raspberrypi.local "unzip -o ${projectName}.zip \
    && cd ${projectName} \
    && pip3 install -r requirements.txt"
}

start() {
  echo "Starting service on raspberry pi..."
  ssh pi@raspberrypi.local "pkill python3 \
    && nohup python3 lib/main.py &"
}

main() {
  prepare
  package
  build_and_deploy
  # start
}

main