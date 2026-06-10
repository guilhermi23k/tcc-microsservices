package br.uva.tcc.estoque.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.List;

/** Evento publicado pelo Estoque após processar a reserva. */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class EstoqueProcessadoEvento implements Serializable {
    private Long pedidoId;
    private Long clienteId;
    private boolean sucesso;
    private String motivo;
    private BigDecimal total;
    private List<ItemConfirmado> itens;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ItemConfirmado implements Serializable {
        private Long produtoId;
        private Integer quantidade;
        private BigDecimal precoUnitario;
    }
}
