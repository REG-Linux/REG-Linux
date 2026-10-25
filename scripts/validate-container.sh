#!/bin/bash
# Validate container runtime availability
# Usage: validate-container.sh [docker|podman]

set -e

CONTAINER="${1:-docker}"

case "$CONTAINER" in
    docker)
        if ! command -v docker >/dev/null 2>&1; then
            echo "Error: Docker is not installed. Please install Docker first." >&2
            exit 1
        fi
        if ! docker info >/dev/null 2>&1; then
            echo "Warning: Docker daemon is not running. Some operations may fail." >&2
        fi
        echo "Docker is available: $(docker --version)"
        ;;
    podman)
        if ! command -v podman >/dev/null 2>&1; then
            echo "Error: Podman is not installed. Please install Podman first." >&2
            exit 1
        fi
        echo "Podman is available: $(podman --version)"
        # Podman doesn't require daemon, but check if it works
        if ! podman info >/dev/null 2>&1; then
            echo "Warning: Podman info command failed. Rootless mode may have limitations." >&2
        fi
        ;;
    *)
        echo "Error: Invalid container runtime '$CONTAINER'. Must be 'docker' or 'podman'." >&2
        exit 1
        ;;
esac

exit 0
