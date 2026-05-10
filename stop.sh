#!/bin/bash
# ============================================
# EdilEngine - Stop servizi locali
# ============================================
set -e

echo "🛑 Fermando EdilEngine..."
docker compose down

echo ""
echo "✅ Servizi fermati."
echo ""
echo "I dati del database sono PRESERVATI (volume pgdata)."
echo "Per cancellare anche i dati del DB:"
echo "   docker compose down -v"