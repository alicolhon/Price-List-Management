#!/usr/bin/env bash
# MA-SMS deployment helper — run this on the VM after cloning the repo.
# Requires Podman + podman-compose (or the built-in `podman compose` in Podman 4.4+).
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$APP_DIR/data"

echo "================================================"
echo "  MA-SMS Price List Management — Deploy"
echo "================================================"
echo ""

# ── 1. Check Podman ──────────────────────────────────────────────────────────
if ! command -v podman &>/dev/null; then
    echo "Podman not found. Installing (Debian/Ubuntu)..."
    sudo apt-get update -y
    sudo apt-get install -y podman
    echo "Podman installed: $(podman --version)"
fi

# Prefer built-in `podman compose` (Podman >= 4.4), fall back to podman-compose package
COMPOSE_CMD=""
if podman compose version &>/dev/null 2>&1; then
    COMPOSE_CMD="podman compose"
elif command -v podman-compose &>/dev/null; then
    COMPOSE_CMD="podman-compose"
else
    echo "podman-compose not found. Installing..."
    sudo apt-get install -y podman-compose 2>/dev/null \
        || pip3 install --user podman-compose
    COMPOSE_CMD="podman-compose"
fi

echo "Using compose command: $COMPOSE_CMD"
echo ""

# ── 2. Rootless port-80 check ────────────────────────────────────────────────
# Rootless Podman cannot bind to ports < 1024 by default.
# If running as non-root, set sysctl or use port 8080.
if [ "$(id -u)" -ne 0 ]; then
    UNPRIV_PORT=$(sysctl -n net.ipv4.ip_unprivileged_port_start 2>/dev/null || echo 1024)
    if [ "$UNPRIV_PORT" -gt 80 ]; then
        echo "NOTE: Rootless Podman cannot bind port 80 (ip_unprivileged_port_start=$UNPRIV_PORT)."
        echo "Options:"
        echo "  A) Allow port 80:  sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80"
        echo "     (add to /etc/sysctl.d/99-podman.conf to persist)"
        echo "  B) Change the port in docker-compose.yml from '80:80' to '8080:80'"
        echo "     then access the app at http://HOST:8080"
        echo "  C) Run this script with sudo for rootful Podman."
        echo ""
        read -r -p "Apply option A automatically now? [y/N] " answer
        if [[ "$answer" =~ ^[Yy]$ ]]; then
            sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80
            echo 'net.ipv4.ip_unprivileged_port_start=80' | sudo tee /etc/sysctl.d/99-podman-port80.conf
        else
            echo "Continuing — edit docker-compose.yml if port 80 fails."
        fi
        echo ""
    fi
fi

# ── 3. Check Excel file ──────────────────────────────────────────────────────
mkdir -p "$DATA_DIR"

if [ ! -f "$DATA_DIR/price_list.xlsb" ]; then
    echo "ERROR: Price list not found at:"
    echo "  $DATA_DIR/price_list.xlsb"
    echo ""
    echo "Copy it from your local machine:"
    echo "  scp 'B_2. Lighting Technology 42026DE21.xlsb' \\"
    echo "      USER@$(hostname):$DATA_DIR/price_list.xlsb"
    echo ""
    echo "Then re-run: bash deploy.sh"
    exit 1
fi

echo "Excel file found ($(du -sh "$DATA_DIR/price_list.xlsb" | cut -f1)) — OK"
echo ""

# ── 4. Build and start ───────────────────────────────────────────────────────
cd "$APP_DIR"

echo "Building image (first build: ~5-10 min due to LibreOffice)..."
$COMPOSE_CMD build

echo ""
echo "Starting container..."
$COMPOSE_CMD up -d

# Determine access URL
HOST_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")
PORT=$(grep -E '^\s+-\s+"?[0-9]+:80"?' docker-compose.yml \
    | head -1 | grep -oP '^\s+-\s+"?\K[0-9]+(?=:80)' || echo "80")

echo ""
echo "================================================"
echo "  App is running!"
echo "  URL: http://$HOST_IP:$PORT"
echo "================================================"
echo ""
echo "The price list import runs automatically in the background (~2 min)."
echo ""
echo "Useful commands:"
echo "  Watch logs:   $COMPOSE_CMD logs -f"
echo "  Stop:         $COMPOSE_CMD down"
echo "  Rebuild:      $COMPOSE_CMD up -d --build"
echo "  Force re-import (after replacing the Excel file):"
echo "    curl -X POST http://localhost:$PORT/api/import/run -H 'Content-Type: application/json' -d '{\"force\":true}'"
