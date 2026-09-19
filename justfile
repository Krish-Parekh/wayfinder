# ---- laptop -----------------------------------------------------------------

# Run the MCP tools server alone
tools:
    uv run wayfinder serve-tools

# Run all four servers together on the laptop; Ctrl-C stops the lot
fleet:
    #!/usr/bin/env bash
    set -euo pipefail
    trap 'kill 0' EXIT
    uv run wayfinder serve-tools &
    sleep 3
    uv run python -m wayfinder.route_planner &
    uv run python -m wayfinder.places_researcher &
    uv run python -m wayfinder.food_scout &
    echo "fleet up: tools :8000, route-planner :9001, places-researcher :9002, food-scout :9003"
    wait

# Confirm every specialist is discoverable
cards:
    #!/usr/bin/env bash
    for port in 9001 9002 9003; do
      curl -s "http://127.0.0.1:$port/.well-known/agent-card.json" \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['name'])"
    done

# The reference request from the spec
demo:
    uv run wayfinder plan "Sydney to Melbourne over 4 days by car. Vegetarian, one severe nut allergy, travelling with a 6-year-old, \$1200 budget."

# ---- minikube ---------------------------------------------------------------

# Build the image and push it into every minikube node.
# `minikube image load` silently keeps a stale same-tag image, so remove first.
image:
    #!/usr/bin/env bash
    set -euo pipefail
    docker build -q -t wayfinder:dev .
    for n in $(kubectl get nodes -o name | cut -d/ -f2); do
      minikube ssh -p cka-learn -n "$n" -- docker rmi -f wayfinder:dev >/dev/null 2>&1 || true
    done
    minikube image load wayfinder:dev -p cka-learn

# Apply every manifest; generates the Secret from ~/.aws/credentials first
deploy:
    ./scripts/make-secret.sh
    kubectl apply -f k8s/namespace.yml -f k8s/secret.yml -f k8s/configmap.yml
    kubectl apply -f k8s/tools.yml -f k8s/route-planner.yml -f k8s/places-researcher.yml -f k8s/food-scout.yml
    kubectl apply -f k8s/pdb.yml -f k8s/networkpolicy.yml
    kubectl wait -n wayfinder --for=condition=ready pod -l role=specialist --timeout=180s

# Forward the three specialists to localhost so `just demo` hits the cluster
forward:
    #!/usr/bin/env bash
    set -euo pipefail
    trap 'kill 0' EXIT
    kubectl port-forward -n wayfinder svc/route-planner 9001:9001 &
    kubectl port-forward -n wayfinder svc/places-researcher 9002:9002 &
    kubectl port-forward -n wayfinder svc/food-scout 9003:9003 &
    echo "forwarding :9001 :9002 :9003 -> cluster; Ctrl-C stops"
    wait
