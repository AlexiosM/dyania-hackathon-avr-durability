#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT"

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
    echo "Virtual environment not found: $ROOT/.venv"
    exit 1
fi

PYTHON="$ROOT/.venv/bin/python"

if ! command -v ollama >/dev/null 2>&1; then
    echo "Ollama is not installed or is not in PATH"
    exit 1
fi

if ! ollama list | grep -q '^medgemma:latest'; then
    echo "medgemma:latest is not available in Ollama"
    exit 1
fi

mkdir -p "$ROOT/data/processed"

echo "========================================"
echo "1. CLEAN DATA"
echo "========================================"

"$PYTHON" "$ROOT/scripts/clean_data.py"

echo
echo "========================================"
echo "2. EXTRACT PATIENTS WITH MEDGEMMA"
echo "========================================"

"$PYTHON" "$ROOT/scripts/extract_patients.py"

echo
echo "========================================"
echo "3. ENRICH WITH LABS AND MEDICATIONS"
echo "========================================"

"$PYTHON" "$ROOT/scripts/enrich_patients.py"

echo
echo "========================================"
echo "4. VALIDATE"
echo "========================================"

"$PYTHON" "$ROOT/scripts/validate.py"

echo
echo "========================================"
echo "PIPELINE COMPLETE"
echo "========================================"

echo "patients.json:"
echo "  $ROOT/data/processed/patients.json"

echo "enriched_patients.json:"
echo "  $ROOT/data/processed/enriched_patients.json"

echo "validation_report.json:"
echo "  $ROOT/data/processed/validation_report.json"
