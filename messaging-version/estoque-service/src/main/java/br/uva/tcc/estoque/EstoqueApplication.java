package br.uva.tcc.estoque;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Serviço de Estoque - versão assíncrona.
 * Consome eventos de pedido criado, processa a reserva e publica
 * o resultado de volta, sem manter conexão síncrona com o Pedidos.
 */
@SpringBootApplication
public class EstoqueApplication {
    public static void main(String[] args) {
        SpringApplication.run(EstoqueApplication.class, args);
    }
}
