package br.uva.tcc.pedidos.service;

import br.uva.tcc.pedidos.domain.ItemPedido;
import br.uva.tcc.pedidos.domain.Pedido;
import br.uva.tcc.pedidos.domain.PedidoRepository;
import br.uva.tcc.pedidos.domain.PedidoStatus;
import br.uva.tcc.pedidos.dto.CriarPedidoRequest;
import br.uva.tcc.pedidos.dto.EstoqueProcessadoEvento;
import br.uva.tcc.pedidos.dto.PedidoCriadoEvento;
import br.uva.tcc.pedidos.messaging.PedidoEventPublisher;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Lógica de pedidos na versão assíncrona.
 *
 * criar(): persiste o pedido como CRIADO e PUBLICA um evento.
 *          Retorna imediatamente - NÃO espera o estoque.
 *
 * aplicarResultadoEstoque(): chamado de forma assíncrona quando
 *          o evento de resultado chega do Estoque. Atualiza o
 *          pedido para CONFIRMADO ou REJEITADO (consistência eventual).
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class PedidoService {

    private final PedidoRepository repository;
    private final PedidoEventPublisher publisher;

    @Transactional
    public Pedido criar(CriarPedidoRequest request) {
        Pedido pedido = Pedido.builder()
                .clienteId(request.getClienteId())
                .itens(new ArrayList<>(request.getItens().stream()
                        .map(i -> new ItemPedido(i.getProdutoId(), i.getQuantidade(), null))
                        .toList()))
                .total(BigDecimal.ZERO)
                .status(PedidoStatus.CRIADO)
                .criadoEm(LocalDateTime.now())
                .build();
        pedido = repository.save(pedido);

        List<PedidoCriadoEvento.ItemEvento> itensEvento = pedido.getItens().stream()
                .map(i -> new PedidoCriadoEvento.ItemEvento(i.getProdutoId(), i.getQuantidade()))
                .toList();
        publisher.publicarPedidoCriado(
                new PedidoCriadoEvento(pedido.getId(), pedido.getClienteId(), itensEvento));

        return pedido;
    }

    @Transactional
    public void aplicarResultadoEstoque(EstoqueProcessadoEvento evento) {
        // Trata graciosamente mensagens órfãs: se o pedido não existe mais
        // (ex.: banco recriado entre execuções), apenas registra e ignora,
        // em vez de lançar exceção e enviar a mensagem para a DLQ.
        Optional<Pedido> optPedido = repository.findById(evento.getPedidoId());
        if (optPedido.isEmpty()) {
            log.warn("Resultado recebido para pedido inexistente ({}), ignorando. "
                    + "Provavelmente mensagem órfã de execução anterior.", evento.getPedidoId());
            return;
        }
        Pedido pedido = optPedido.get();

        // Idempotência: se já foi processado, ignora (evita reprocessamento
        // de mensagem duplicada, comum em sistemas de mensageria).
        if (pedido.getStatus() != PedidoStatus.CRIADO) {
            log.debug("Pedido {} já processado (status {}), ignorando evento",
                    pedido.getId(), pedido.getStatus());
            return;
        }

        if (evento.isSucesso()) {
            pedido.setTotal(evento.getTotal());
            List<ItemPedido> itens = new ArrayList<>();
            for (EstoqueProcessadoEvento.ItemConfirmado i : evento.getItens()) {
                itens.add(new ItemPedido(i.getProdutoId(), i.getQuantidade(), i.getPrecoUnitario()));
            }
            pedido.setItens(itens);
            pedido.setStatus(PedidoStatus.CONFIRMADO);
        } else {
            pedido.setStatus(PedidoStatus.REJEITADO);
            pedido.setMotivoRejeicao(evento.getMotivo());
        }
        repository.save(pedido);
        log.debug("Pedido {} atualizado para {}", pedido.getId(), pedido.getStatus());
    }

    @Transactional(readOnly = true)
    public Pedido buscar(Long id) {
        return repository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Pedido não encontrado: " + id));
    }
}