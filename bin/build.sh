#!/usr/bin/env bash
set -ex

tag=us.gcr.io/w210-incorpbot/$1

pushd $2
docker build -t ${tag} .
popd
