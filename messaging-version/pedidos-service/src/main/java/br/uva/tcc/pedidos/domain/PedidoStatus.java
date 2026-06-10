package br.uva.tcc.pedidos.domain;

/**
 * Estados do pedido na versão assíncrona.
 * Diferentemente da versão REST, o pedido permanece em CRIADO
 * por um intervalo até que o evento de resultado do estoque
 * seja consumido (consistência eventual).
 */
public enum PedidoStatus {
    CRIADO,
    CONFIRMADO,
    REJEITADO
}
