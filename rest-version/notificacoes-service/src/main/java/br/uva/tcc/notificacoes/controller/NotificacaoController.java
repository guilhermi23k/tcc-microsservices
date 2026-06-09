package br.uva.tcc.notificacoes.controller;

import br.uva.tcc.notificacoes.domain.Notificacao;
import br.uva.tcc.notificacoes.dto.NotificacaoRequest;
import br.uva.tcc.notificacoes.service.NotificacaoService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/notificacoes")
@RequiredArgsConstructor
public class NotificacaoController {

    private final NotificacaoService service;

    @PostMapping
    public ResponseEntity<Notificacao> registrar(@Valid @RequestBody NotificacaoRequest req) {
        Notificacao n = service.registrar(req);
        return ResponseEntity.status(HttpStatus.CREATED).body(n);
    }
}
