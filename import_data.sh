#!/bin/bash
# Quick helper: copy the Excel file to the data folder and trigger import

ROOT="$(cd "$(dirname "$0")" && pwd)"
EXCEL_SRC="/home/ai-station01/Desktop/Claude-skills/skills/MA-SMS/B_2. Lighting Technology 42026DE21.xlsb"

mkdir -p "$ROOT/backend/data"
echo "Copying Excel file..."
cp "$EXCEL_SRC" "$ROOT/backend/data/price_list.xlsb"
echo "Done. Starting import via API..."
curl -s -X POST "http://localhost:8000/api/import/run?force=true" | python3 -m json.tool
