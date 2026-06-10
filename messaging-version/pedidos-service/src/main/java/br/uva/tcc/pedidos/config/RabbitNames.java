package br.uva.tcc.pedidos.config;

/**
 * Nomes centralizados de exchanges, filas e routing keys.
 * Mantidos em um único lugar para evitar divergência entre serviços.
 */
public final class RabbitNames {
    private RabbitNames() {}

    // Exchange onde Pedidos publica o evento de pedido criado
    public static final String PEDIDOS_EXCHANGE = "pedidos.exchange";
    public static final String RK_PEDIDO_CRIADO = "pedido.criado";

    // Exchange onde Estoque publica o resultado do processamento
    public static final String ESTOQUE_EXCHANGE = "estoque.exchange";
    public static final String RK_ESTOQUE_PROCESSADO = "estoque.processado";

    // Fila que Pedidos consome para receber o resultado do estoque
    public static final String FILA_PEDIDOS_RESULTADO = "pedidos.estoque-processado";

    // Dead Letter Exchange e fila para mensagens que falham repetidamente
    public static final String DLX = "tcc.dlx";
    public static final String FILA_PEDIDOS_DLQ = "pedidos.estoque-processado.dlq";
    public static final String RK_DLQ_PEDIDOS = "dlq.pedidos";
}
