#!/usr/bin/env bash
# Roda N repetições do cenário 4 MSG com restart completo entre cada uma.
# Cria pedidos de seed antes de cada execução do k6.
# Uso: ./run-msg-cenario4.sh <repeticoes>
set -euo pipefail

REPS="${1:-5}"
RATE="${RATE:-50}"
DURATION="${DURATION:-5m}"
SEED_MAX_ID="${SEED_MAX_ID:-200}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
mkdir -p "$RESULTS_DIR"

echo "=== Bateria MSG Cenário 4: $REPS reps, ${RATE} req/s, ${DURATION}, seed=${SEED_MAX_ID} pedidos ==="
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

  # Seed: cria SEED_MAX_ID pedidos e aguarda processamento
  echo "    Criando $SEED_MAX_ID pedidos de seed..."
  for i in $(seq 1 "$SEED_MAX_ID"); do
    PRODUTO_ID=$(( (RANDOM % 100) + 1 ))
    CLIENTE_ID=$(( (RANDOM % 1000) + 1 ))
    QUANTIDADE=$(( (RANDOM % 3) + 1 ))
    curl -s -o /dev/null -X POST http://localhost:8081/pedidos \
      -H "Content-Type: application/json" \
      -d "{\"clienteId\": $CLIENTE_ID, \"itens\": [{\"produtoId\": $PRODUTO_ID, \"quantidade\": $QUANTIDADE}]}"
  done

  # Aguarda o RabbitMQ processar todos os pedidos do seed
  echo "    Aguardando processamento do seed (30s)..."
  sleep 30

  # Roda o benchmark
  cd "$SCRIPT_DIR"
  local_out="$RESULTS_DIR/cenario4_msg_rep${rep}.csv"
  echo "    Rodando k6 (${RATE} req/s, ${DURATION})..."
  VERSAO=msg k6 run --out "csv=$local_out" \
    -e RATE="$RATE" -e DURATION="$DURATION" -e SEED_MAX_ID="$SEED_MAX_ID" \
    "$SCRIPT_DIR/scenarios/cenario4-consulta.js"

  echo "    CSV salvo: $local_out"
  echo ""
done

echo "=== Concluído. $REPS CSVs em $RESULTS_DIR ==="
echo "Agora rode o REST:"
echo "  docker compose --profile messaging down -v"
echo "  docker compose --profile rest up -d"
echo "  sleep 40"
echo "  # seed REST"
echo "  for i in \$(seq 1 $SEED_MAX_ID); do"
echo "    curl -s -o /dev/null -X POST http://localhost:8081/pedidos \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"clienteId\": 1, \"itens\": [{\"produtoId\": 1, \"quantidade\": 1}]}'"
echo "  done"
echo "  sleep 10"
echo "  RATE=$RATE DURATION=$DURATION SEED_MAX_ID=$SEED_MAX_ID ./run-all.sh rest 4 $REPS"
