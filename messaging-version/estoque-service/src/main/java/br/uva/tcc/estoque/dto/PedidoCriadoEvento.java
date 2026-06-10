package br.uva.tcc.estoque.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.List;

/** Evento consumido do Pedidos. */
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
