# Análise dos Resultados

Script que processa os CSVs gerados pelos benchmarks (k6) e produz
tabelas estatísticas e gráficos para os capítulos 5 e 6 do TCC.

## Instalar dependências

```bash
cd analysis
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

(ou, sem venv: `pip install -r requirements.txt --break-system-packages`)

## Rodar

```bash
python3 analisar.py
```

O script lê de `../benchmarks/results/` e escreve em `output/`:

- `tabela_resumo.csv` — média, desvio, P50, P95, P99, throughput, taxa de sucesso
  por cenário e versão (cole no TCC como tabela)
- `testes_hipotese.txt` — comparação estatística REST vs MSG (Shapiro-Wilk +
  t pareado ou Mann-Whitney) por cenário
- `grafico_cenario1_latencia.png` — boxplot de latência REST vs MSG
- `grafico_cenario2_throughput.png` — throughput ao longo da carga
- `grafico_cenario3_resiliencia.png` — sucesso ao longo do tempo (com janela de falha)
- `grafico_cenario4_latencia.png` — boxplot de latência de consulta
- `grafico_comparativo_latencia.png` — barras comparando latência média por cenário

## Padrão de nomes esperado

Os CSVs devem seguir: `cenario<N>_<versao>_rep<R>.csv`
(gerado automaticamente pelo run-all.sh)
