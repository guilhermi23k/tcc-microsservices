# TCC — Análise Comparativa: REST vs Mensageria em Microsserviços

Artefatos de software do TCC que compara empiricamente comunicação síncrona (REST) e assíncrona (RabbitMQ) em arquiteturas de microsserviços.

## Estrutura

```
├── docker-compose.yml          # orquestração (perfis: rest, messaging)
├── rest-version/               # versão síncrona (COMPLETA)
│   ├── pedidos-service/        # porta 8081 - orquestrador
│   ├── estoque-service/        # porta 8082 - reserva de itens
│   └── notificacoes-service/   # porta 8083 - notificações
├── messaging-version/          # versão assíncrona (A IMPLEMENTAR)
├── benchmarks/                 # scripts k6 (A IMPLEMENTAR)
└── analysis/                   # análise Python (A IMPLEMENTAR)
```

## Executar versão REST

```bash
docker compose --profile rest up -d --build
```

Aguarde ~1 min. Validação:

```bash
# Health checks
curl http://localhost:8081/actuator/health
curl http://localhost:8082/actuator/health
curl http://localhost:8083/actuator/health

# Criar pedido
curl -X POST http://localhost:8081/pedidos \
  -H "Content-Type: application/json" \
  -d '{"clienteId": 1, "itens": [{"produtoId": 1, "quantidade": 2}]}'

# Consultar pedido
curl http://localhost:8081/pedidos/1
```

Parar: `docker compose --profile rest down` (com `-v` para zerar os bancos).

## Stack

Java 17 · Spring Boot 3.2 · PostgreSQL 16 · RabbitMQ 3.13 · Docker Compose · k6 · cAdvisor
