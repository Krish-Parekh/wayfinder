# Run the MCP tools server alone
tools:
    uv run wayfinder serve-tools

# Run all four servers together; Ctrl-C stops the lot
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
