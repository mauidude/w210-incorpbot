#!/usr/bin/env bash
set -ex

helm upgrade --install $1 .k8s/$1
