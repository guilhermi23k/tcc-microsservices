package br.uva.tcc.pedidos.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ReservaEstoqueResponse {
    private boolean sucesso;
    private String motivo;
    private BigDecimal total;
    private List<ItemConfirmadoDto> itens;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ItemConfirmadoDto {
        private Long produtoId;
        private Integer quantidade;
        private BigDecimal precoUnitario;
    }
}
