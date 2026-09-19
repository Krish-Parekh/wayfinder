#!/usr/bin/env bash
# Build k8s/secret.yml from the default profile in ~/.aws/credentials.
set -euo pipefail
key=$(aws configure get aws_access_key_id)
secret=$(aws configure get aws_secret_access_key)
cat > "$(dirname "$0")/../k8s/secret.yml" <<YAML
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
echo "wrote k8s/secret.yml (gitignored)"
