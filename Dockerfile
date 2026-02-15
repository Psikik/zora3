# ABOUTME: Template for the agent container image.
# ABOUTME: setup.sh injects a toolchain snippet between the markers to produce Dockerfile.

FROM docker/sandbox-templates:claude-code

USER root

# --- TOOLCHAIN_START ---
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*
# --- TOOLCHAIN_END ---

USER agent

COPY loop.sh /loop.sh

ENTRYPOINT ["/loop.sh"]
