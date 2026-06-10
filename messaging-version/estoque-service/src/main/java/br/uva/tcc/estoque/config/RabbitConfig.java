package br.uva.tcc.estoque.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Topologia RabbitMQ do Estoque.
 *   CONSOME de estoque.pedido-criado (vinda de pedidos.exchange)
 *   PUBLICA em estoque.exchange (rk estoque.processado)
 * A fila de consumo tem DLQ.
 */
@Configuration
public class RabbitConfig {

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

    @Bean
    public TopicExchange pedidosExchange() {
        return new TopicExchange(RabbitNames.PEDIDOS_EXCHANGE, true, false);
    }

    @Bean
    public TopicExchange estoqueExchange() {
        return new TopicExchange(RabbitNames.ESTOQUE_EXCHANGE, true, false);
    }

    @Bean
    public DirectExchange deadLetterExchange() {
        return new DirectExchange(RabbitNames.DLX, true, false);
    }

    @Bean
    public Queue filaEstoque() {
        return QueueBuilder.durable(RabbitNames.FILA_ESTOQUE)
                .withArgument("x-dead-letter-exchange", RabbitNames.DLX)
                .withArgument("x-dead-letter-routing-key", RabbitNames.RK_DLQ_ESTOQUE)
                .build();
    }

    @Bean
    public Binding bindingEstoque(Queue filaEstoque, TopicExchange pedidosExchange) {
        return BindingBuilder.bind(filaEstoque)
                .to(pedidosExchange)
                .with(RabbitNames.RK_PEDIDO_CRIADO);
    }

    @Bean
    public Queue filaEstoqueDlq() {
        return QueueBuilder.durable(RabbitNames.FILA_ESTOQUE_DLQ).build();
    }

    @Bean
    public Binding bindingEstoqueDlq(Queue filaEstoqueDlq, DirectExchange deadLetterExchange) {
        return BindingBuilder.bind(filaEstoqueDlq)
                .to(deadLetterExchange)
                .with(RabbitNames.RK_DLQ_ESTOQUE);
    }
}
