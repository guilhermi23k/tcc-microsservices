package br.uva.tcc.notificacoes;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Serviço de Notificações - versão REST síncrona.
 * Recebe e persiste notificações de pedidos.
 */
@SpringBootApplication
public class NotificacoesApplication {

    public static void main(String[] args) {
        SpringApplication.run(NotificacoesApplication.class, args);
    }
}
