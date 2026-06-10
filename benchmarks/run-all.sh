#!/usr/bin/env bash
# Orquestra a execução dos benchmarks.
#
# Uso:
#   ./run-all.sh <versao> <cenario> <repeticoes>
#
#   versao:     rest | msg
#   cenario:    1 | 2 | 3 | 4 | all
#   repeticoes: número de repetições (padrão 10)
#
# Exemplos:
#   ./run-all.sh rest 1 10      # cenário 1, REST, 10 repetições
#   ./run-all.sh msg all 30     # todos os cenários, MSG, 30 repetições
#
# Pré-requisito: a versão correspondente deve estar no ar
#   docker compose --profile rest up -d      (para versao=rest)
#   docker compose --profile messaging up -d (para versao=msg)

set -euo pipefail

VERSAO="${1:-rest}"
CENARIO="${2:-all}"
REPS="${3:-10}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
mkdir -p "$RESULTS_DIR"

# Nome do container de estoque conforme a versão (para o cenário 3)
if [ "$VERSAO" = "rest" ]; then
  ESTOQUE_CONTAINER="estoque-rest"
else
  ESTOQUE_CONTAINER="estoque-msg"
fi

run_cenario() {
  local n="$1"
  local script="$2"
  local extra_env="${3:-}"

  for rep in $(seq 1 "$REPS"); do
    local out="$RESULTS_DIR/cenario${n}_${VERSAO}_rep${rep}.csv"
    echo ">>> Cenário $n | versão $VERSAO | repetição $rep/$REPS"

    if [ "$n" = "3" ]; then
      # Cenário de falha: dispara o k6 em background e injeta a falha.
      VERSAO="$VERSAO" k6 run --out "csv=$out" $extra_env "$SCRIPT_DIR/scenarios/$script" &
      local k6pid=$!
      # Aos 2 min, derruba o estoque por 30s.
      sleep 120
      echo "    >> Derrubando $ESTOQUE_CONTAINER (falha injetada)"
      docker stop "$ESTOQUE_CONTAINER" >/dev/null
      sleep 30
      echo "    >> Religando $ESTOQUE_CONTAINER"
      docker start "$ESTOQUE_CONTAINER" >/dev/null
      wait $k6pid
    else
      VERSAO="$VERSAO" k6 run --out "csv=$out" $extra_env "$SCRIPT_DIR/scenarios/$script"
    fi

    echo "    CSV salvo em $out"
    # Intervalo entre repetições (estabilização)
    sleep 30
  done
}

case "$CENARIO" in
  1) run_cenario 1 "cenario1-carga-constante.js" ;;
  2) run_cenario 2 "cenario2-carga-crescente.js" ;;
  3) run_cenario 3 "cenario3-falha-injetada.js" ;;
  4) run_cenario 4 "cenario4-consulta.js" "-e SEED_MAX_ID=500" ;;
  all)
    run_cenario 1 "cenario1-carga-constante.js"
    run_cenario 2 "cenario2-carga-crescente.js"
    run_cenario 3 "cenario3-falha-injetada.js"
    run_cenario 4 "cenario4-consulta.js" "-e SEED_MAX_ID=500"
    ;;
  *) echo "Cenário inválido: $CENARIO (use 1|2|3|4|all)"; exit 1 ;;
esac

echo ""
echo "=== Concluído. CSVs em $RESULTS_DIR ==="
