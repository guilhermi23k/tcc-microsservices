package br.uva.tcc.estoque.messaging;

import br.uva.tcc.estoque.config.RabbitNames;
import br.uva.tcc.estoque.dto.PedidoCriadoEvento;
import br.uva.tcc.estoque.service.EstoqueService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

/**
 * Consome o evento de pedido criado e dispara o processamento.
 *
 * Ponto-chave do cenário 3 (falha): se este serviço estiver fora
 * do ar, as mensagens se ACUMULAM na fila estoque.pedido-criado
 * e são processadas quando o serviço volta - SEM perda de pedidos.
 * É o contraste direto com a versão REST, onde a falha derruba o pedido.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class PedidoCriadoListener {

    private final EstoqueService estoqueService;

    @RabbitListener(queues = RabbitNames.FILA_ESTOQUE)
    public void aoReceber(PedidoCriadoEvento evento) {
        log.debug("Pedido criado recebido para processamento: {}", evento.getPedidoId());
        estoqueService.processar(evento);
    }
}
