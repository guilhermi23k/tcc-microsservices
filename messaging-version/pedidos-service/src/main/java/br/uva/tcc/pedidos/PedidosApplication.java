package br.uva.tcc.pedidos;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Serviço de Pedidos - versão assíncrona (mensageria).
 * Publica eventos de pedido criado e consome eventos de resultado
 * do processamento de estoque, sem bloquear o cliente.
 */
@SpringBootApplication
public class PedidosApplication {
    public static void main(String[] args) {
        SpringApplication.run(PedidosApplication.class, args);
    }
}
