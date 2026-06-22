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

# ── 2. Port check ────────────────────────────────────────────────────────────
# Port 4444 is > 1024, so rootless Podman can bind it without any sysctl changes.

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
PORT=$(grep -E '^\s+-\s+"?[0-9]+:[0-9]+"?' docker-compose.yml \
    | head -1 | grep -oP '"?\K[0-9]+(?=:[0-9])' || echo "4444")

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
