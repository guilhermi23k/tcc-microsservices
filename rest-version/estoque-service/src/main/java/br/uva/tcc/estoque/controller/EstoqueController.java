package br.uva.tcc.estoque.controller;

import br.uva.tcc.estoque.dto.ReservaRequest;
import br.uva.tcc.estoque.dto.ReservaResponse;
import br.uva.tcc.estoque.service.EstoqueService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/estoque")
@RequiredArgsConstructor
public class EstoqueController {

    private final EstoqueService service;

    @PostMapping("/reservas")
    public ResponseEntity<ReservaResponse> reservar(@Valid @RequestBody ReservaRequest request) {
        try {
            return ResponseEntity.ok(service.reservar(request));
        } catch (EstoqueService.ReservaInvalidaException e) {
            // Reserva inválida é regra de negócio, não erro técnico:
            // retornamos 200 com sucesso=false.
            return ResponseEntity.ok(ReservaResponse.falha(e.getMessage()));
        }
    }
}
