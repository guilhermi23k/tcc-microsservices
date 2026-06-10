package br.uva.tcc.pedidos.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Map;

/**
 * Configuração da topologia RabbitMQ do serviço de Pedidos.
 *
 * Pedidos:
 *   - PUBLICA em pedidos.exchange (rk pedido.criado)  -> consumido pelo Estoque
 *   - CONSOME de pedidos.estoque-processado            -> resultado vindo do Estoque
 *
 * A fila de consumo tem Dead Letter Queue: se o processamento
 * falhar e a mensagem for rejeitada, ela vai para a DLQ em vez
 * de ser reprocessada infinitamente.
 */
@Configuration
public class RabbitConfig {

    // Converte objetos Java <-> JSON nas mensagens
    @Bean
    public MessageConverter jsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory cf, MessageConverter conv) {
        RabbitTemplate t = new RabbitTemplate(cf);
        t.setMessageConverter(conv);
        return t;
    }

    // ----- Exchange onde Pedidos publica -----
    @Bean
    public TopicExchange pedidosExchange() {
        return new TopicExchange(RabbitNames.PEDIDOS_EXCHANGE, true, false);
    }

    // ----- Exchange de resultado (declarada também aqui para garantir existência) -----
    @Bean
    public TopicExchange estoqueExchange() {
        return new TopicExchange(RabbitNames.ESTOQUE_EXCHANGE, true, false);
    }

    // ----- Dead Letter Exchange -----
    @Bean
    public DirectExchange deadLetterExchange() {
        return new DirectExchange(RabbitNames.DLX, true, false);
    }

    // ----- Fila de resultado (com DLQ configurada) -----
    @Bean
    public Queue filaResultado() {
        return QueueBuilder.durable(RabbitNames.FILA_PEDIDOS_RESULTADO)
                .withArgument("x-dead-letter-exchange", RabbitNames.DLX)
                .withArgument("x-dead-letter-routing-key", RabbitNames.RK_DLQ_PEDIDOS)
                .build();
    }

    @Bean
    public Binding bindingResultado(Queue filaResultado, TopicExchange estoqueExchange) {
        return BindingBuilder.bind(filaResultado)
                .to(estoqueExchange)
                .with(RabbitNames.RK_ESTOQUE_PROCESSADO);
    }

    // ----- Dead Letter Queue -----
    @Bean
    public Queue filaDlq() {
        return QueueBuilder.durable(RabbitNames.FILA_PEDIDOS_DLQ).build();
    }

    @Bean
    public Binding bindingDlq(Queue filaDlq, DirectExchange deadLetterExchange) {
        return BindingBuilder.bind(filaDlq)
                .to(deadLetterExchange)
                .with(RabbitNames.RK_DLQ_PEDIDOS);
    }
}
