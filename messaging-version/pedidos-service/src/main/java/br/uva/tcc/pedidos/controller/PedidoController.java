package br.uva.tcc.pedidos.controller;

import br.uva.tcc.pedidos.domain.Pedido;
import br.uva.tcc.pedidos.dto.CriarPedidoRequest;
import br.uva.tcc.pedidos.service.PedidoService;
import jakarta.persistence.EntityNotFoundException;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Na versão assíncrona, POST /pedidos retorna 202 ACCEPTED com o
 * pedido em status CRIADO - o processamento ocorre depois.
 * O cliente consulta GET /pedidos/{id} para ver o status final
 * (polling), conforme descrito na metodologia (cenário 4).
 */
@RestController
@RequestMapping("/pedidos")
@RequiredArgsConstructor
public class PedidoController {

    private final PedidoService service;

    @PostMapping
    public ResponseEntity<Pedido> criar(@Valid @RequestBody CriarPedidoRequest request) {
        Pedido pedido = service.criar(request);
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(pedido);
    }

    @GetMapping("/{id}")
    public Pedido buscar(@PathVariable Long id) {
        return service.buscar(id);
    }

    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<String> naoEncontrado(EntityNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(e.getMessage());
    }
}
