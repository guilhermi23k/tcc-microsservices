package br.uva.tcc.pedidos.domain;

/**
 * Estados possíveis de um pedido.
 *   CRIADO      - recém-criado, ainda não validado.
 *   CONFIRMADO  - estoque reservado e notificação disparada.
 *   REJEITADO   - estoque insuficiente ou falha de serviço.
 */
public enum PedidoStatus {
    CRIADO,
    CONFIRMADO,
    REJEITADO
}
