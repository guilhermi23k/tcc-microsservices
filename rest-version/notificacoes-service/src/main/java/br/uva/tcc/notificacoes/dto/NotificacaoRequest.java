package br.uva.tcc.notificacoes.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class NotificacaoRequest {

    @NotNull
    private Long pedidoId;

    @NotNull
    private Long clienteId;

    @NotBlank
    private String tipo;

    @NotBlank
    private String mensagem;
}
