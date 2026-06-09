package br.uva.tcc.estoque.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ReservaRequest {

    @NotNull
    private Long pedidoId;

    @NotEmpty
    @Valid
    private List<ItemReservaDto> itens;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ItemReservaDto {
        @NotNull
        private Long produtoId;

        @NotNull
        private Integer quantidade;
    }
}
