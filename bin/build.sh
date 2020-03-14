#!/usr/bin/env bash
set -e

tag=us.gcr.io/w210-incorpbot/$1

pushd $2
docker build -t ${tag} $1
popd
