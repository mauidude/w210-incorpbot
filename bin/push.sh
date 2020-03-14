#!/usr/bin/env bash
set -ex

tag=us.gcr.io/w210-incorpbot/$1
docker push ${tag}
