#!/usr/bin/env bash
# Roda N repetições do cenário 4 REST com seed de pedidos entre cada uma.
# Uso: ./run-rest-cenario4.sh <repeticoes>
set -euo pipefail

REPS="${1:-5}"
RATE="${RATE:-50}"
DURATION="${DURATION:-5m}"
SEED_MAX_ID="${SEED_MAX_ID:-200}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
mkdir -p "$RESULTS_DIR"

echo "=== Bateria REST Cenário 4: $REPS reps, ${RATE} req/s, ${DURATION}, seed=${SEED_MAX_ID} pedidos ==="
echo ""

for rep in $(seq 1 "$REPS"); do
  echo ">>> Repetição $rep/$REPS — limpando estado..."

  # Limpa bancos (igual ao run-all.sh)
  docker exec postgres-pedidos psql -U tcc -d pedidos -c "TRUNCATE TABLE pedidos CASCADE; ALTER SEQUENCE pedidos_id_seq RESTART WITH 1;" > /dev/null 2>&1 || true
  docker exec postgres-estoque psql -U tcc -d estoque -c "UPDATE produtos SET quantidade_estoque = 1000000, versao = 0;" > /dev/null 2>&1 || true
  docker exec postgres-notificacoes psql -U tcc -d notificacoes -c "TRUNCATE TABLE notificacoes CASCADE;" > /dev/null 2>&1 || true
  echo "    Estado limpo."

  # Seed: cria SEED_MAX_ID pedidos
  echo "    Criando $SEED_MAX_ID pedidos de seed..."
  for i in $(seq 1 "$SEED_MAX_ID"); do
    PRODUTO_ID=$(( (RANDOM % 100) + 1 ))
    CLIENTE_ID=$(( (RANDOM % 1000) + 1 ))
    QUANTIDADE=$(( (RANDOM % 3) + 1 ))
    curl -s -o /dev/null -X POST http://localhost:8081/pedidos \
      -H "Content-Type: application/json" \
      -d "{\"clienteId\": $CLIENTE_ID, \"itens\": [{\"produtoId\": $PRODUTO_ID, \"quantidade\": $QUANTIDADE}]}"
  done

  # Pausa pra garantir que todos os pedidos foram persistidos
  echo "    Aguardando persistência do seed (10s)..."
  sleep 10

  # Roda o benchmark
  local_out="$RESULTS_DIR/cenario4_rest_rep${rep}.csv"
  echo "    Rodando k6 (${RATE} req/s, ${DURATION})..."
  VERSAO=rest k6 run --out "csv=$local_out" \
    -e RATE="$RATE" -e DURATION="$DURATION" -e SEED_MAX_ID="$SEED_MAX_ID" \
    "$SCRIPT_DIR/scenarios/cenario4-consulta.js"

  echo "    CSV salvo: $local_out"
  echo ""
  sleep 10
done

echo "=== Concluído. $REPS CSVs em $RESULTS_DIR ==="