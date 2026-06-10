// Cenário 1: Carga constante (criação de pedidos).
// Avalia latência em regime estável. 50 req/s por 5 min + 1 min warm-up.
// Métrica principal: latência fim-a-fim (média + P50/P95/P99).
import { Trend, Rate } from 'k6/metrics';
import { criarPedido } from '../lib/helpers.js';

const latencia = new Trend('latencia_pedido', true);
const sucessoRate = new Rate('sucesso_pedido');

export const options = {
  scenarios: {
    carga_constante: {
      executor: 'constant-arrival-rate',
      rate: Number(__ENV.RATE || 50),   // req/s
      timeUnit: '1s',
      duration: __ENV.DURATION || '5m',
      preAllocatedVUs: 100,
      maxVUs: 500,
    },
  },
  // Warm-up: descarta o primeiro minuto na análise (feito no script Python).
  // Aqui marcamos thresholds informativos.
  thresholds: {
    sucesso_pedido: ['rate>0.95'],
  },
};

export default function () {
  const inicio = Date.now();
  const r = criarPedido();
  const fim = Date.now();
  latencia.add(fim - inicio);
  sucessoRate.add(r.sucesso);
}
