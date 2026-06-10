package br.uva.tcc.pedidos.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.List;

/**
 * Evento publicado quando um pedido é criado.
 * Consumido pelo serviço de Estoque para efetuar a reserva.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PedidoCriadoEvento implements Serializable {
    private Long pedidoId;
    private Long clienteId;
    private List<ItemEvento> itens;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ItemEvento implements Serializable {
        private Long produtoId;
        private Integer quantidade;
    }
}
