package br.uva.tcc.pedidos.messaging;

import br.uva.tcc.pedidos.config.RabbitNames;
import br.uva.tcc.pedidos.dto.PedidoCriadoEvento;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Component;

/**
 * Publica eventos de pedido criado na exchange.
 * Esta é a essência do modelo assíncrono: o pedido é publicado
 * e o método retorna imediatamente, SEM esperar o Estoque processar.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class PedidoEventPublisher {

    private final RabbitTemplate rabbitTemplate;

    public void publicarPedidoCriado(PedidoCriadoEvento evento) {
        rabbitTemplate.convertAndSend(
                RabbitNames.PEDIDOS_EXCHANGE,
                RabbitNames.RK_PEDIDO_CRIADO,
                evento
        );
        log.debug("Evento pedido.criado publicado para pedido {}", evento.getPedidoId());
    }
}
