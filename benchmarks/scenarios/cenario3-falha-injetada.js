// Cenário 3: Falha injetada em serviço dependente (Estoque).
// Carga constante de 50 req/s por 6 min. O run-all.sh derruba o
// estoque aos 2min por 30s. Mede taxa de sucesso ao longo do tempo
// e comportamento de recuperação.
//
// Diferença esperada:
//   REST: durante a falha, pedidos são REJEITADOS (falha em cascata).
//   MSG:  durante a falha, pedidos ficam CRIADO (na fila) e completam
//         após o estoque voltar - polling pode dar TIMEOUT durante a janela.
import { Trend, Rate, Counter } from 'k6/metrics';
import { criarPedido } from '../lib/helpers.js';

const latencia = new Trend('latencia_pedido', true);
const sucessoRate = new Rate('sucesso_pedido');
const confirmados = new Counter('pedidos_confirmados');
const rejeitados = new Counter('pedidos_rejeitados');
const timeouts = new Counter('pedidos_timeout');

export const options = {
  scenarios: {
    falha_injetada: {
      executor: 'constant-arrival-rate',
      rate: Number(__ENV.RATE || 50),
      timeUnit: '1s',
      duration: __ENV.DURATION || '6m',
      preAllocatedVUs: 100,
      maxVUs: 500,
    },
  },
};

export default function () {
  const inicio = Date.now();
  const r = criarPedido();
  const fim = Date.now();
  latencia.add(fim - inicio);
  sucessoRate.add(r.sucesso);

  if (r.statusFinal === 'CONFIRMADO') confirmados.add(1);
  else if (r.statusFinal === 'REJEITADO') rejeitados.add(1);
  else if (r.statusFinal === 'TIMEOUT_POLLING') timeouts.add(1);
}
