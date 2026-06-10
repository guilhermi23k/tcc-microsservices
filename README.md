# TCC — Análise Comparativa: REST vs Mensageria em Microsserviços

Compara empiricamente comunicação síncrona (REST) e assíncrona (RabbitMQ) em microsserviços.

## Estrutura

```
├── docker-compose.yml          # perfis: rest, messaging
├── rest-version/               # versão síncrona (COMPLETA)
│   ├── pedidos-service/        # 8081 - orquestrador (saga orquestrada)
│   ├── estoque-service/        # 8082 - reserva (lock pessimista)
│   └── notificacoes-service/   # 8083 - notificações
├── messaging-version/          # versão assíncrona (COMPLETA)
│   ├── pedidos-service/        # 8081 - publica evento, consome resultado
│   ├── estoque-service/        # 8082 - consome pedido, publica resultado
│   └── notificacoes-service/   # 8083 - consome resultado (pub/sub)
├── benchmarks/                 # scripts k6 (A IMPLEMENTAR)
└── analysis/                   # análise Python (A IMPLEMENTAR)
```

## Executar versão REST

```bash
docker compose --profile rest up -d --build
```

Criação retorna o pedido já CONFIRMADO (síncrono).

## Executar versão Messaging

```bash
docker compose --profile messaging up -d --build
```

Criação retorna 202 ACCEPTED com status CRIADO; o processamento ocorre
de forma assíncrona. Consulte GET /pedidos/{id} para ver o status final.

Console RabbitMQ: http://localhost:15672 (tcc/tcc)

### Validar messaging

```bash
# Cria pedido (retorna 202, status CRIADO)
curl -i -X POST http://localhost:8081/pedidos \
  -H "Content-Type: application/json" \
  -d '{"clienteId": 1, "itens": [{"produtoId": 1, "quantidade": 2}]}'

# Aguarde ~1s e consulte: status deve estar CONFIRMADO
curl http://localhost:8081/pedidos/1
```

## Arquitetura

- **REST**: saga orquestrada. Pedidos chama Estoque e Notificações via HTTP, bloqueante.
- **Messaging**: saga coreografada. Eventos via RabbitMQ (topic exchanges), com Dead Letter Queues. Pedidos publica `pedido.criado`; Estoque consome, processa e publica `estoque.processado`; Pedidos e Notificações consomem o resultado (publish-subscribe).

## Stack

Java 17 · Spring Boot 3.2 · Spring AMQP · PostgreSQL 16 · RabbitMQ 3.13 · Docker Compose · k6 · cAdvisor
