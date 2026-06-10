// Funções compartilhadas pelos cenários de benchmark.
import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8081';
// VERSAO controla o comportamento de medição: 'rest' ou 'msg'
export const VERSAO = __ENV.VERSAO || 'rest';

// Gera um corpo de pedido com itens aleatórios (produtos 1..100).
export function gerarPedido() {
  const numItens = Math.floor(Math.random() * 3) + 1; // 1 a 3 itens
  const itens = [];
  for (let i = 0; i < numItens; i++) {
    itens.push({
      produtoId: Math.floor(Math.random() * 100) + 1,
      quantidade: Math.floor(Math.random() * 3) + 1,
    });
  }
  return { clienteId: Math.floor(Math.random() * 1000) + 1, itens };
}

// Cria um pedido. Em REST, o POST já volta CONFIRMADO/REJEITADO.
// Em MSG, o POST volta 202 com CRIADO; fazemos polling até status final
// para medir a latência fim-a-fim de forma justa.
// Retorna { sucesso: boolean, statusFinal: string }.
export function criarPedido() {
  const payload = JSON.stringify(gerarPedido());
  const params = { headers: { 'Content-Type': 'application/json' } };

  const res = http.post(`${BASE_URL}/pedidos`, payload, params);

  if (VERSAO === 'rest') {
    // Resposta síncrona: o corpo já tem o status final.
    const ok = check(res, { 'POST 2xx': (r) => r.status >= 200 && r.status < 300 });
    let statusFinal = 'DESCONHECIDO';
    try { statusFinal = JSON.parse(res.body).status; } catch (e) {}
    return { sucesso: ok, statusFinal };
  }

  // MSG: espera 202 e faz polling no GET até sair de CRIADO.
  if (res.status !== 202) {
    return { sucesso: false, statusFinal: 'ERRO_POST' };
  }
  let id;
  try { id = JSON.parse(res.body).id; } catch (e) { return { sucesso: false, statusFinal: 'ERRO_PARSE' }; }

  // Polling: até ~5s (50 tentativas de 100ms).
  for (let tentativa = 0; tentativa < 50; tentativa++) {
    const g = http.get(`${BASE_URL}/pedidos/${id}`);
    if (g.status === 200) {
      let st = 'CRIADO';
      try { st = JSON.parse(g.body).status; } catch (e) {}
      if (st === 'CONFIRMADO' || st === 'REJEITADO') {
        return { sucesso: true, statusFinal: st };
      }
    }
    // espera curta antes da próxima tentativa
    sleepMs(100);
  }
  // Não confirmou no tempo limite (relevante no cenário 3 com estoque fora).
  return { sucesso: false, statusFinal: 'TIMEOUT_POLLING' };
}

// Consulta um pedido existente (cenário 4). Retorna boolean de sucesso.
export function consultarPedido(id) {
  const res = http.get(`${BASE_URL}/pedidos/${id}`);
  return check(res, { 'GET 200': (r) => r.status === 200 });
}

// k6 não tem sleep em ms nativo no import padrão; emulamos com busy-wait curto
// via http nenhum. Usamos o sleep do k6 em segundos fracionados.
import { sleep } from 'k6';
function sleepMs(ms) {
  sleep(ms / 1000);
}
