package br.uva.tcc.notificacoes.service;

import br.uva.tcc.notificacoes.domain.Notificacao;
import br.uva.tcc.notificacoes.domain.NotificacaoRepository;
import br.uva.tcc.notificacoes.dto.EstoqueProcessadoEvento;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
@Slf4j
public class NotificacaoService {

    private final NotificacaoRepository repository;

    @Transactional
    public void processar(EstoqueProcessadoEvento evento) {
        // Só notifica pedidos confirmados.
        if (!evento.isSucesso()) {
            log.debug("Pedido {} não confirmado, sem notificação", evento.getPedidoId());
            return;
        }

        Notificacao n = Notificacao.builder()
                .pedidoId(evento.getPedidoId())
                .clienteId(evento.getClienteId())
                .tipo("PEDIDO_CONFIRMADO")
                .mensagem("Seu pedido foi confirmado!")
                .enviadaEm(LocalDateTime.now())
                .build();
        repository.save(n);
        log.debug("Notificação registrada para pedido {}", evento.getPedidoId());
    }
}
