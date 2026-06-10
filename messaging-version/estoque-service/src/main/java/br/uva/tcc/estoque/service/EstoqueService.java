package br.uva.tcc.estoque.service;

import br.uva.tcc.estoque.config.RabbitNames;
import br.uva.tcc.estoque.domain.Produto;
import br.uva.tcc.estoque.domain.ProdutoRepository;
import br.uva.tcc.estoque.dto.EstoqueProcessadoEvento;
import br.uva.tcc.estoque.dto.PedidoCriadoEvento;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Processa o evento de pedido criado: tenta reservar o estoque
 * e publica o resultado. Diferentemente da versão REST, não há
 * resposta HTTP - o resultado é publicado como novo evento.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class EstoqueService {

    private final ProdutoRepository repository;
    private final RabbitTemplate rabbitTemplate;

    @Transactional
    public void processar(PedidoCriadoEvento evento) {
        EstoqueProcessadoEvento resultado = tentarReservar(evento);
        rabbitTemplate.convertAndSend(
                RabbitNames.ESTOQUE_EXCHANGE,
                RabbitNames.RK_ESTOQUE_PROCESSADO,
                resultado
        );
        log.debug("Resultado publicado para pedido {}: sucesso={}",
                evento.getPedidoId(), resultado.isSucesso());
    }

    private EstoqueProcessadoEvento tentarReservar(PedidoCriadoEvento evento) {
        List<EstoqueProcessadoEvento.ItemConfirmado> confirmados = new ArrayList<>();
        BigDecimal total = BigDecimal.ZERO;

        for (PedidoCriadoEvento.ItemEvento item : evento.getItens()) {
            Optional<Produto> opt = repository.findByIdForUpdate(item.getProdutoId());

            if (opt.isEmpty()) {
                return falha(evento, "Produto " + item.getProdutoId() + " não encontrado");
            }
            Produto produto = opt.get();

            if (produto.getQuantidadeEstoque() < item.getQuantidade()) {
                return falha(evento, "Estoque insuficiente para produto " + item.getProdutoId());
            }

            produto.setQuantidadeEstoque(produto.getQuantidadeEstoque() - item.getQuantidade());
            repository.save(produto);

            BigDecimal subtotal = produto.getPreco().multiply(BigDecimal.valueOf(item.getQuantidade()));
            total = total.add(subtotal);
            confirmados.add(new EstoqueProcessadoEvento.ItemConfirmado(
                    produto.getId(), item.getQuantidade(), produto.getPreco()));
        }

        return new EstoqueProcessadoEvento(
                evento.getPedidoId(), evento.getClienteId(),
                true, "ok", total, confirmados);
    }

    private EstoqueProcessadoEvento falha(PedidoCriadoEvento evento, String motivo) {
        return new EstoqueProcessadoEvento(
                evento.getPedidoId(), evento.getClienteId(),
                false, motivo, BigDecimal.ZERO, List.of());
    }
}
