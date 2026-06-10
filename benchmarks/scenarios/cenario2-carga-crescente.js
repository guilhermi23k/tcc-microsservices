// Cenário 2: Carga crescente (criação de pedidos).
// Rampa de 10 a 500 req/s ao longo de 10 min. Identifica ponto de saturação.
// Métrica principal: throughput máximo sustentado.
import { Trend, Rate } from 'k6/metrics';
import { criarPedido } from '../lib/helpers.js';

const latencia = new Trend('latencia_pedido', true);
const sucessoRate = new Rate('sucesso_pedido');

export const options = {
  scenarios: {
    carga_crescente: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 200,
      maxVUs: 1000,
      stages: [
        { target: Number(__ENV.MAX_RATE || 500), duration: __ENV.DURATION || '10m' },
      ],
    },
  },
};

export default function () {
  const inicio = Date.now();
  const r = criarPedido();
  const fim = Date.now();
  latencia.add(fim - inicio);
  sucessoRate.add(r.sucesso);
}
