package br.uva.tcc.notificacoes.messaging;

import br.uva.tcc.notificacoes.config.RabbitNames;
import br.uva.tcc.notificacoes.dto.EstoqueProcessadoEvento;
import br.uva.tcc.notificacoes.service.NotificacaoService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class EstoqueProcessadoListener {

    private final NotificacaoService service;

    @RabbitListener(queues = RabbitNames.FILA_NOTIFICACOES)
    public void aoReceber(EstoqueProcessadoEvento evento) {
        log.debug("Evento de estoque processado recebido para pedido {}", evento.getPedidoId());
        service.processar(evento);
    }
}
