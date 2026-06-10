package br.uva.tcc.pedidos.messaging;

import br.uva.tcc.pedidos.config.RabbitNames;
import br.uva.tcc.pedidos.dto.EstoqueProcessadoEvento;
import br.uva.tcc.pedidos.service.PedidoService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

/**
 * Consome o evento de resultado publicado pelo Estoque e atualiza
 * o status do pedido (CONFIRMADO ou REJEITADO).
 *
 * Se o processamento lançar exceção, a mensagem é rejeitada e,
 * graças à configuração de DLQ, encaminhada para a Dead Letter Queue
 * em vez de reprocessada indefinidamente.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class EstoqueResultadoListener {

    private final PedidoService pedidoService;

    @RabbitListener(queues = RabbitNames.FILA_PEDIDOS_RESULTADO)
    public void aoReceberResultado(EstoqueProcessadoEvento evento) {
        log.debug("Resultado de estoque recebido para pedido {}: sucesso={}",
                evento.getPedidoId(), evento.isSucesso());
        pedidoService.aplicarResultadoEstoque(evento);
    }
}
