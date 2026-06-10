# Benchmarks (k6)

Scripts de carga para os quatro cenários experimentais do TCC.

## Instalar o k6 (no WSL/Ubuntu)

```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt update
sudo apt install k6
```

Confirme: `k6 version`

## Como rodar

A versão correspondente precisa estar no ar:

```bash
# Para benchmarks REST:
docker compose --profile rest up -d

# Para benchmarks Messaging:
docker compose --profile messaging up -d
```

Depois, da pasta benchmarks/:

```bash
# Sintaxe: ./run-all.sh <versao> <cenario> <repeticoes>

./run-all.sh rest 1 10      # cenário 1, REST, 10 repetições
./run-all.sh msg 3 10       # cenário 3 (falha), Messaging, 10 repetições
./run-all.sh rest all 30    # todos, REST, 30 repetições
```

Os CSVs são salvos em `results/` com o padrão:
`cenario<N>_<versao>_rep<R>.csv`

## Parâmetros ajustáveis

Se a máquina saturar cedo demais, reduza as taxas via variáveis de ambiente
editando o run-all.sh ou passando -e. Exemplos:

- Cenário 1/3/4: `RATE` (req/s, padrão 50)
- Cenário 2: `MAX_RATE` (pico da rampa, padrão 500)
- Todos: `DURATION` (ex: '3m')

> Importante: se você alterar os parâmetros, atualize a seção de
> metodologia do TCC para refletir os valores realmente usados.

## Cenário 3 (falha injetada)

O run-all.sh derruba automaticamente o container de estoque aos 2 min
por 30s e religa. Não precisa fazer nada manualmente - só garanta que o
Docker está acessível pelo terminal.

## Cenário 4 (consulta)

Antes de medir, é preciso ter pedidos cadastrados. Crie uma carga inicial:

```bash
# cria 500 pedidos para popular a base antes do cenário 4
for i in $(seq 1 500); do
  curl -s -X POST http://localhost:8081/pedidos \
    -H "Content-Type: application/json" \
    -d '{"clienteId": 1, "itens": [{"produtoId": 1, "quantidade": 1}]}' > /dev/null
done
```

(Na versão msg, aguarde alguns segundos após o loop para os pedidos
serem processados antes de iniciar o cenário 4.)
