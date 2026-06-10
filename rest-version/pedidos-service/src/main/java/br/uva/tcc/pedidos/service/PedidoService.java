package br.uva.tcc.pedidos.service;

import br.uva.tcc.pedidos.client.EstoqueClient;
import br.uva.tcc.pedidos.client.NotificacoesClient;
import br.uva.tcc.pedidos.domain.ItemPedido;
import br.uva.tcc.pedidos.domain.Pedido;
import br.uva.tcc.pedidos.domain.PedidoRepository;
import br.uva.tcc.pedidos.domain.PedidoStatus;
import br.uva.tcc.pedidos.dto.CriarPedidoRequest;
import br.uva.tcc.pedidos.dto.NotificacaoRequest;
import br.uva.tcc.pedidos.dto.ReservaEstoqueRequest;
import br.uva.tcc.pedidos.dto.ReservaEstoqueResponse;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Orquestra a criação de um pedido na versão síncrona.
 *
 * Fluxo:
 *   1. Persiste o pedido com status CRIADO.
 *   2. Chama Estoque sincronamente para reservar.
 *   3. Se reservou: CONFIRMADO + Notificação síncrona.
 *   4. Se não: REJEITADO.
 *
 * O cliente HTTP fica BLOQUEADO até toda a cadeia terminar.
 * A latência percebida = Pedidos + Estoque + Notificações.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class PedidoService {

    private final PedidoRepository repository;
    private final EstoqueClient estoqueClient;
    private final NotificacoesClient notificacoesClient;

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

        ReservaEstoqueRequest reservaReq = montarReservaRequest(pedido);
        ReservaEstoqueResponse reservaResp;
        try {
            reservaResp = estoqueClient.reservar(reservaReq);
        } catch (Exception e) {
            log.warn("Falha ao chamar Estoque para pedido {}: {}", pedido.getId(), e.getMessage());
            pedido.setStatus(PedidoStatus.REJEITADO);
            String motivo = "Estoque indisponível: " + e.getMessage();
            pedido.setMotivoRejeicao(motivo.length() > 500 ? motivo.substring(0, 500) : motivo);
            return repository.save(pedido);
        }

        if (!reservaResp.isSucesso()) {
            pedido.setStatus(PedidoStatus.REJEITADO);
            pedido.setMotivoRejeicao(reservaResp.getMotivo());
            return repository.save(pedido);
        }

        pedido.setTotal(reservaResp.getTotal());
        List<ItemPedido> itensConfirmados = new ArrayList<>();
        for (ReservaEstoqueResponse.ItemConfirmadoDto i : reservaResp.getItens()) {
            itensConfirmados.add(new ItemPedido(i.getProdutoId(), i.getQuantidade(), i.getPrecoUnitario()));
        }
        pedido.setItens(itensConfirmados);
        pedido.setStatus(PedidoStatus.CONFIRMADO);

        try {
            notificacoesClient.enviar(new NotificacaoRequest(
                    pedido.getId(),
                    pedido.getClienteId(),
                    "PEDIDO_CONFIRMADO",
                    "Seu pedido foi confirmado!"
            ));
        } catch (Exception e) {
            log.warn("Falha ao enviar notificação do pedido {}: {}", pedido.getId(), e.getMessage());
        }

        return repository.save(pedido);
    }

    @Transactional(readOnly = true)
    public Pedido buscar(Long id) {
        return repository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Pedido não encontrado: " + id));
    }

    private ReservaEstoqueRequest montarReservaRequest(Pedido pedido) {
        List<ReservaEstoqueRequest.ItemReservaDto> itens = pedido.getItens().stream()
                .map(i -> new ReservaEstoqueRequest.ItemReservaDto(i.getProdutoId(), i.getQuantidade()))
                .toList();
        return new ReservaEstoqueRequest(pedido.getId(), itens);
    }
}
