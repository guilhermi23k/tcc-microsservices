package br.uva.tcc.pedidos.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class NotificacaoRequest {
    private Long pedidoId;
    private Long clienteId;
    private String tipo;
    private String mensagem;
}
