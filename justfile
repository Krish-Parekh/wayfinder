tools:
    uv run wayfinder serve-tools

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

cards:
    #!/usr/bin/env bash
    for port in 9001 9002 9003; do
      curl -s "http://127.0.0.1:$port/.well-known/agent-card.json" \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['name'])"
    done

demo:
    uv run wayfinder plan "Sydney to Melbourne over 4 days by car. Vegetarian, one severe nut allergy, travelling with a 6-year-old, \$1200 budget."

region := "ap-southeast-2"
ecr := "682761213103.dkr.ecr.ap-southeast-2.amazonaws.com/wayfinder"

image target="minikube":
    #!/usr/bin/env bash
    set -euo pipefail
    case "{{target}}" in
      minikube)
        docker build -q -t wayfinder:dev .
        for n in $(kubectl get nodes -o name | cut -d/ -f2); do
          minikube ssh -p cka-learn -n "$n" -- docker rmi -f wayfinder:dev >/dev/null 2>&1 || true
        done
        minikube image load wayfinder:dev -p cka-learn ;;
      eks)
        aws ecr get-login-password --region {{region}} \
          | docker login --username AWS --password-stdin "$(cut -d/ -f1 <<< {{ecr}})"
        docker buildx build --platform linux/amd64 -t {{ecr}}:dev --push . ;;
      *) echo "unknown target {{target}}" >&2; exit 1 ;;
    esac

deploy target="minikube":
    #!/usr/bin/env bash
    set -euo pipefail
    if [ "{{target}}" = minikube ]; then ./scripts/make-secret.sh; fi
    kubectl apply -k k8s/overlays/{{target}}
    kubectl wait -n wayfinder --for=condition=ready pod -l role=specialist --timeout=420s

forward:
    #!/usr/bin/env bash
    set -euo pipefail
    trap 'kill 0' EXIT
    kubectl port-forward -n wayfinder svc/route-planner 9001:9001 &
    kubectl port-forward -n wayfinder svc/places-researcher 9002:9002 &
    kubectl port-forward -n wayfinder svc/food-scout 9003:9003 &
    echo "forwarding :9001 :9002 :9003 -> cluster; Ctrl-C stops"
    wait

infra-up:
    terraform -chdir=infra init -input=false
    terraform -chdir=infra apply -input=false

kubeconfig:
    aws eks update-kubeconfig --region {{region}} --name wayfinder

infra-down:
    -kubectl delete namespace wayfinder --timeout=180s
    terraform -chdir=infra destroy -input=false
