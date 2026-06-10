package br.uva.tcc.notificacoes.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Topologia RabbitMQ do Notificacoes.
 *   CONSOME de notificacoes.estoque-processado (de estoque.exchange)
 * Repare: a MESMA exchange estoque.exchange alimenta DUAS filas
 * (a do Pedidos e a do Notificacoes). Isso é publish-subscribe:
 * um evento, múltiplos consumidores independentes.
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
    public TopicExchange estoqueExchange() {
        return new TopicExchange(RabbitNames.ESTOQUE_EXCHANGE, true, false);
    }

    @Bean
    public DirectExchange deadLetterExchange() {
        return new DirectExchange(RabbitNames.DLX, true, false);
    }

    @Bean
    public Queue filaNotificacoes() {
        return QueueBuilder.durable(RabbitNames.FILA_NOTIFICACOES)
                .withArgument("x-dead-letter-exchange", RabbitNames.DLX)
                .withArgument("x-dead-letter-routing-key", RabbitNames.RK_DLQ_NOTIFICACOES)
                .build();
    }

    @Bean
    public Binding bindingNotificacoes(Queue filaNotificacoes, TopicExchange estoqueExchange) {
        return BindingBuilder.bind(filaNotificacoes)
                .to(estoqueExchange)
                .with(RabbitNames.RK_ESTOQUE_PROCESSADO);
    }

    @Bean
    public Queue filaNotificacoesDlq() {
        return QueueBuilder.durable(RabbitNames.FILA_NOTIFICACOES_DLQ).build();
    }

    @Bean
    public Binding bindingNotificacoesDlq(Queue filaNotificacoesDlq, DirectExchange deadLetterExchange) {
        return BindingBuilder.bind(filaNotificacoesDlq)
                .to(deadLetterExchange)
                .with(RabbitNames.RK_DLQ_NOTIFICACOES);
    }
}
