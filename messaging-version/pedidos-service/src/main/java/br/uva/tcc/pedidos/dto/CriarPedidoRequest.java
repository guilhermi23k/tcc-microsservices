package br.uva.tcc.pedidos.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

@Data
public class CriarPedidoRequest {
    @NotNull
    private Long clienteId;

    @NotEmpty
    @Valid
    private List<ItemPedidoRequest> itens;
}
