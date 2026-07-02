#!/usr/bin/env bash
# Roda N repetições do cenário 2 MSG com restart completo entre cada uma.
# Uso: ./run-msg-cenario2.sh <repeticoes>
set -euo pipefail

REPS="${1:-5}"
MAX_RATE="${MAX_RATE:-100}"
DURATION="${DURATION:-5m}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
mkdir -p "$RESULTS_DIR"

echo "=== Bateria MSG Cenário 2: $REPS reps, ramp até ${MAX_RATE} req/s, ${DURATION} ==="
echo ""

for rep in $(seq 1 "$REPS"); do
  echo ">>> Repetição $rep/$REPS — reiniciando ambiente..."

  # Restart completo (limpa volumes = banco + filas zerados)
  cd "$PROJECT_DIR"
  docker compose --profile messaging down -v > /dev/null 2>&1
  docker compose --profile messaging up -d --build > /dev/null 2>&1

  # Espera o sistema ficar pronto
  echo "    Aguardando sistema subir (90s)..."
  sleep 90

  # Confirma que está respondendo
  for tentativa in $(seq 1 10); do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/actuator/health | grep -q "200"; then
      break
    fi
    sleep 5
  done

  # Roda o benchmark
  cd "$SCRIPT_DIR"
  local_out="$RESULTS_DIR/cenario2_msg_rep${rep}.csv"
  echo "    Rodando k6 (ramp até ${MAX_RATE} req/s, ${DURATION})..."
  VERSAO=msg k6 run --out "csv=$local_out" \
    -e MAX_RATE="$MAX_RATE" -e DURATION="$DURATION" \
    "$SCRIPT_DIR/scenarios/cenario2-carga-crescente.js"

  echo "    CSV salvo: $local_out"
  echo ""
done

echo "=== Concluído. $REPS CSVs em $RESULTS_DIR ==="
echo "Agora rode o REST:"
echo "  docker compose --profile messaging down"
echo "  docker compose --profile rest up -d"
echo "  sleep 40"
echo "  MAX_RATE=$MAX_RATE DURATION=$DURATION ./run-all.sh rest 2 $REPS"
