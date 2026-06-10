package br.uva.tcc.estoque.config;

public final class RabbitNames {
    private RabbitNames() {}

    public static final String PEDIDOS_EXCHANGE = "pedidos.exchange";
    public static final String RK_PEDIDO_CRIADO = "pedido.criado";

    public static final String ESTOQUE_EXCHANGE = "estoque.exchange";
    public static final String RK_ESTOQUE_PROCESSADO = "estoque.processado";

    // Fila que o Estoque consome
    public static final String FILA_ESTOQUE = "estoque.pedido-criado";

    // DLQ do Estoque
    public static final String DLX = "tcc.dlx";
    public static final String FILA_ESTOQUE_DLQ = "estoque.pedido-criado.dlq";
    public static final String RK_DLQ_ESTOQUE = "dlq.estoque";
}
