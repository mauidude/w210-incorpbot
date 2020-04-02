#!/usr/bin/env bash

set -ex

# install kubectl
curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.14.6/2019-08-22/bin/linux/amd64/kubectl
chmod +x ./kubectl
mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
kubectl version --short --client

# install aws iam authenticator
curl -o aws-iam-authenticator https://amazon-eks.s3.us-west-2.amazonaws.com/1.15.10/2020-02-22/bin/linux/amd64/aws-iam-authenticator
chmod +x ./aws-iam-authenticator
mkdir -p $HOME/bin && cp ./aws-iam-authenticator $HOME/bin/aws-iam-authenticator && export PATH=$PATH:$HOME/bin
aws-iam-authenticator help

# kubectl auth
mkdir -p /var/lib/buildkite-agent/.kube
aws eks --region us-west-2 update-kubeconfig --name incorpbot --kubeconfig /var/lib/buildkite-agent/.kube/config
chown buildkite-agent:buildkite-agent /var/lib/buildkite-agent/.kube/config

# install helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
