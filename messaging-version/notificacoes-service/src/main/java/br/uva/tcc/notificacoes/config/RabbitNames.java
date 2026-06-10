package br.uva.tcc.notificacoes.config;

public final class RabbitNames {
    private RabbitNames() {}

    public static final String ESTOQUE_EXCHANGE = "estoque.exchange";
    public static final String RK_ESTOQUE_PROCESSADO = "estoque.processado";

    public static final String FILA_NOTIFICACOES = "notificacoes.estoque-processado";

    public static final String DLX = "tcc.dlx";
    public static final String FILA_NOTIFICACOES_DLQ = "notificacoes.estoque-processado.dlq";
    public static final String RK_DLQ_NOTIFICACOES = "dlq.notificacoes";
}
