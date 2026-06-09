package br.uva.tcc.estoque.service;

import br.uva.tcc.estoque.domain.Produto;
import br.uva.tcc.estoque.domain.ProdutoRepository;
import br.uva.tcc.estoque.dto.ReservaRequest;
import br.uva.tcc.estoque.dto.ReservaResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Lógica de reserva de estoque. Reserva atômica: se qualquer item
 * não tiver estoque, a transação inteira é desfeita.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class EstoqueService {

    private final ProdutoRepository repository;

    @Transactional
    public ReservaResponse reservar(ReservaRequest request) {
        List<ReservaResponse.ItemConfirmadoDto> confirmados = new ArrayList<>();
        BigDecimal total = BigDecimal.ZERO;

        for (ReservaRequest.ItemReservaDto item : request.getItens()) {
            Optional<Produto> opt = repository.findByIdForUpdate(item.getProdutoId());

            if (opt.isEmpty()) {
                throw new ReservaInvalidaException(
                        "Produto " + item.getProdutoId() + " não encontrado");
            }

            Produto produto = opt.get();

            if (produto.getQuantidadeEstoque() < item.getQuantidade()) {
                throw new ReservaInvalidaException(
                        "Estoque insuficiente para produto " + item.getProdutoId());
            }

            produto.setQuantidadeEstoque(produto.getQuantidadeEstoque() - item.getQuantidade());
            repository.save(produto);

            BigDecimal subtotal = produto.getPreco()
                    .multiply(BigDecimal.valueOf(item.getQuantidade()));
            total = total.add(subtotal);

            confirmados.add(new ReservaResponse.ItemConfirmadoDto(
                    produto.getId(), item.getQuantidade(), produto.getPreco()));
        }

        log.debug("Reserva concluída para pedido {}: total {}", request.getPedidoId(), total);
        return new ReservaResponse(true, "ok", total, confirmados);
    }

    public static class ReservaInvalidaException extends RuntimeException {
        public ReservaInvalidaException(String motivo) {
            super(motivo);
        }
    }
}
