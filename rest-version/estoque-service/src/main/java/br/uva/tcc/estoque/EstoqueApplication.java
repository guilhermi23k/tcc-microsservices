package br.uva.tcc.estoque;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Serviço de Estoque - versão REST síncrona.
 * Expõe endpoints HTTP para reserva de itens de pedidos.
 */
@SpringBootApplication
public class EstoqueApplication {

    public static void main(String[] args) {
        SpringApplication.run(EstoqueApplication.class, args);
    }
}
