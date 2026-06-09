package br.uva.tcc.pedidos.client;

import br.uva.tcc.pedidos.dto.ReservaEstoqueRequest;
import br.uva.tcc.pedidos.dto.ReservaEstoqueResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

/**
 * Cliente HTTP síncrono para o serviço de Estoque.
 * O método reservar() BLOQUEIA até a resposta (ou timeout).
 * Se o Estoque cair, a falha propaga - comportamento observado
 * no cenário 3 dos experimentos.
 */
@Component
@Slf4j
public class EstoqueClient {

    private final RestTemplate restTemplate;
    private final String estoqueUrl;

    public EstoqueClient(RestTemplate restTemplate,
                         @Value("${estoque.service.url}") String estoqueUrl) {
        this.restTemplate = restTemplate;
        this.estoqueUrl = estoqueUrl;
    }

    public ReservaEstoqueResponse reservar(ReservaEstoqueRequest request) {
        log.debug("Solicitando reserva de estoque para pedido {}", request.getPedidoId());
        return restTemplate.postForObject(
                estoqueUrl + "/estoque/reservas",
                request,
                ReservaEstoqueResponse.class
        );
    }
}
