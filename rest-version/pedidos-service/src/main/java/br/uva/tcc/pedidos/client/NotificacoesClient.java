package br.uva.tcc.pedidos.client;

import br.uva.tcc.pedidos.dto.NotificacaoRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

/**
 * Cliente HTTP síncrono para o serviço de Notificações.
 */
@Component
@Slf4j
public class NotificacoesClient {

    private final RestTemplate restTemplate;
    private final String notificacoesUrl;

    public NotificacoesClient(RestTemplate restTemplate,
                              @Value("${notificacoes.service.url}") String notificacoesUrl) {
        this.restTemplate = restTemplate;
        this.notificacoesUrl = notificacoesUrl;
    }

    public void enviar(NotificacaoRequest request) {
        log.debug("Enviando notificação para pedido {}", request.getPedidoId());
        restTemplate.postForObject(
                notificacoesUrl + "/notificacoes",
                request,
                Void.class
        );
    }
}
