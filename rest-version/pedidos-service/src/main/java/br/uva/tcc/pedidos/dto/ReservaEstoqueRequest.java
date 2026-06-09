package br.uva.tcc.pedidos.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ReservaEstoqueRequest {
    private Long pedidoId;
    private List<ItemReservaDto> itens;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ItemReservaDto {
        private Long produtoId;
        private Integer quantidade;
    }
}
