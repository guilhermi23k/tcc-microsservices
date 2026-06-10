package br.uva.tcc.notificacoes;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Serviço de Notificações - versão assíncrona.
 * Consome eventos de estoque processado e registra notificações
 * para pedidos confirmados.
 */
@SpringBootApplication
public class NotificacoesApplication {
    public static void main(String[] args) {
        SpringApplication.run(NotificacoesApplication.class, args);
    }
}
