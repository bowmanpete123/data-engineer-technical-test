#!/bin/bash

# Wrapper to run dbt commands inside the core container
# Supports all commands: run, test, seed, snapshot, etc.

if [ $# -eq 0 ]; then
    echo "Usage: $0 [dbt command]"
    echo "Example: $0 run"
    echo "Example: $0 test"
    exit 1
fi

# Pass all arguments directly to dbt inside the container
docker-compose exec core bash -c "cd /opt/src/analytics && dbt $*"
