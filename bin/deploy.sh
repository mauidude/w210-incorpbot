#!/usr/bin/env bash
set -ex

helm upgrade --install --atomic $1 .k8s/$1
