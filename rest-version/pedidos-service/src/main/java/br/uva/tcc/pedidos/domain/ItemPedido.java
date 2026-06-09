package br.uva.tcc.pedidos.domain;

import jakarta.persistence.Embeddable;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * Item de um pedido (objeto-valor embutido).
 */
@Embeddable
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ItemPedido {
    private Long produtoId;
    private Integer quantidade;
    private BigDecimal precoUnitario;
}
