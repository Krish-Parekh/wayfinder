#!/usr/bin/env bash
set -euo pipefail
key=$(aws configure get aws_access_key_id)
secret=$(aws configure get aws_secret_access_key)
cat > "$(dirname "$0")/../k8s/overlays/minikube/secret.yml" <<YAML
apiVersion: v1
kind: Secret
metadata:
  name: bedrock-creds
  namespace: wayfinder
type: Opaque
stringData:
  AWS_ACCESS_KEY_ID: $key
  AWS_SECRET_ACCESS_KEY: "$secret"
YAML
echo "wrote k8s/overlays/minikube/secret.yml (gitignored)"
