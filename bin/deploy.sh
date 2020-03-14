#!/usr/bin/env bash
set -e

helm upgrade --install $1 .k8s/$1
