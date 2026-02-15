#!/bin/bash
# ABOUTME: Orchestration loop that runs Ralph iterations inside a container.
# ABOUTME: Clones a repo, runs Claude in headless mode, pushes after each iteration.
#
# Usage: ./loop.sh [plan] [max_iterations]
# Examples:
#   ./loop.sh              # Build mode, unlimited tasks
#   ./loop.sh 20           # Build mode, max 20 tasks
#   ./loop.sh plan         # Plan mode, unlimited tasks
#   ./loop.sh plan 5       # Plan mode, max 5 tasks
#
# Environment:
#   REPO_URL            - Git repo to clone (required)
#   BRANCH              - Branch to work on (default: main)
#   CLAUDE_CODE_OAUTH_TOKEN - OAuth token for Claude (from ~/.claude/container-token)
#   GH_TOKEN               - GitHub token for gh CLI and git push

set -euo pipefail

# Configure git authentication via GH_TOKEN
if [ -n "${GH_TOKEN:-}" ]; then
    git config --global url."https://x-access-token:${GH_TOKEN}@github.com/".insteadOf "https://github.com/"
fi

# Clone the repo into the workspace
if [ -z "${REPO_URL:-}" ]; then
    echo "Error: REPO_URL is required"
    exit 1
fi

BRANCH="${BRANCH:-main}"

echo "Cloning $REPO_URL (branch: $BRANCH)..."
git clone --branch "$BRANCH" "$REPO_URL" .
echo "Clone complete."

# Parse arguments
if [ "${1:-}" = "plan" ]; then
    MODE="plan"
    PROMPT_FILE="PROMPT_plan.md"
    MAX_ITERATIONS=${2:-0}
elif [[ "${1:-}" =~ ^[0-9]+$ ]]; then
    MODE="build"
    PROMPT_FILE="PROMPT_build.md"
    MAX_ITERATIONS=$1
else
    MODE="build"
    PROMPT_FILE="PROMPT_build.md"
    MAX_ITERATIONS=0
fi

ITERATION=0
CURRENT_BRANCH=$(git branch --show-current)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Mode:   $MODE"
echo "Prompt: $PROMPT_FILE"
echo "Branch: $CURRENT_BRANCH"
[ $MAX_ITERATIONS -gt 0 ] && echo "Max:    $MAX_ITERATIONS iterations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verify prompt file exists
if [ ! -f "$PROMPT_FILE" ]; then
    echo "Error: $PROMPT_FILE not found"
    exit 1
fi

while true; do
    if [ $MAX_ITERATIONS -gt 0 ] && [ $ITERATION -ge $MAX_ITERATIONS ]; then
        echo "Reached max iterations: $MAX_ITERATIONS"
        break
    fi

    cat "$PROMPT_FILE" | claude -p \
        --dangerously-skip-permissions \
        --output-format=stream-json \
        --model opus \
        --verbose

    # Push changes after each iteration
    git push origin "$CURRENT_BRANCH" || {
        echo "Failed to push. Creating remote branch..."
        git push -u origin "$CURRENT_BRANCH"
    }

    ITERATION=$((ITERATION + 1))
    echo -e "\n\n======================== LOOP $ITERATION ========================\n"
done
