// Cenário 4: Consulta de pedido (operação de leitura).
// 50 req/s por 5 min consultando pedidos já existentes.
// Favorece REST (GET direto) vs MSG (que precisaria request-reply).
//
// IMPORTANTE: antes de rodar este cenário, é preciso ter pedidos
// cadastrados. O run-all.sh cria uma carga inicial de pedidos
// e passa o range de IDs válidos via SEED_MAX_ID.
import { Trend, Rate } from 'k6/metrics';
import { consultarPedido } from '../lib/helpers.js';

const latencia = new Trend('latencia_consulta', true);
const sucessoRate = new Rate('sucesso_consulta');

const MAX_ID = Number(__ENV.SEED_MAX_ID || 100);

export const options = {
  scenarios: {
    consulta: {
      executor: 'constant-arrival-rate',
      rate: Number(__ENV.RATE || 50),
      timeUnit: '1s',
      duration: __ENV.DURATION || '5m',
      preAllocatedVUs: 100,
      maxVUs: 500,
    },
  },
  thresholds: {
    sucesso_consulta: ['rate>0.95'],
  },
};

export default function () {
  const id = Math.floor(Math.random() * MAX_ID) + 1;
  const inicio = Date.now();
  const ok = consultarPedido(id);
  const fim = Date.now();
  latencia.add(fim - inicio);
  sucessoRate.add(ok);
}
