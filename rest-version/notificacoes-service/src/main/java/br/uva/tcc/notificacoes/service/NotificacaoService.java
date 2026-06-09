package br.uva.tcc.notificacoes.service;

import br.uva.tcc.notificacoes.domain.Notificacao;
import br.uva.tcc.notificacoes.domain.NotificacaoRepository;
import br.uva.tcc.notificacoes.dto.NotificacaoRequest;
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
    public Notificacao registrar(NotificacaoRequest req) {
        Notificacao n = Notificacao.builder()
                .pedidoId(req.getPedidoId())
                .clienteId(req.getClienteId())
                .tipo(req.getTipo())
                .mensagem(req.getMensagem())
                .enviadaEm(LocalDateTime.now())
                .build();
        n = repository.save(n);
        log.debug("Notificação {} registrada para pedido {}", n.getId(), n.getPedidoId());
        return n;
    }
}
