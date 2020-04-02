#!/usr/bin/env bash
set -ex

helm upgrade --install --set version=${BUILDKITE_COMMIT} $1 .k8s/$1
