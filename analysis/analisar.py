#!/usr/bin/env python3
"""
Análise dos resultados dos benchmarks REST vs Mensageria.

Lê os CSVs gerados pelo k6 (../benchmarks/results/) e produz tabelas
estatísticas e gráficos para os capítulos 5 e 6 do TCC.

Padrão de nomes esperado: cenario<N>_<versao>_rep<R>.csv
"""

import os
import re
import glob
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend sem display (gera arquivos)
import matplotlib.pyplot as plt
from scipy import stats

warnings.filterwarnings("ignore")

# Caminhos
AQUI = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(AQUI, "..", "benchmarks", "results")
OUTPUT_DIR = os.path.join(AQUI, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cores fixas por versão (consistência visual nos gráficos)
COR_REST = "#2563eb"  # azul
COR_MSG = "#dc2626"   # vermelho

PADRAO = re.compile(r"cenario(\d+)_(rest|msg)_rep(\d+)\.csv$")


def descobrir_arquivos():
    """Retorna lista de (caminho, cenario, versao, rep) dos CSVs encontrados."""
    arquivos = []
    for caminho in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.csv"))):
        m = PADRAO.search(os.path.basename(caminho))
        if m:
            arquivos.append((caminho, int(m.group(1)), m.group(2), int(m.group(3))))
    return arquivos


def carregar_latencias(caminho, warmup_s=60):
    """
    Extrai as latências fim-a-fim (iteration_duration) de um CSV do k6,
    descartando o período de warm-up inicial.
    Retorna um array numpy de latências em ms.
    """
    df = pd.read_csv(caminho)
    it = df[df.metric_name == "iteration_duration"].copy()
    if it.empty:
        return np.array([])
    # descarta warm-up: primeiros warmup_s segundos
    t0 = it.timestamp.min()
    duracao_total = it.timestamp.max() - t0
    if duracao_total > warmup_s:
        it = it[it.timestamp >= t0 + warmup_s]
    else:
        # Execução mais curta que o warm-up (ex.: teste rápido).
        # Usa todos os dados em vez de descartar tudo.
        print(f"  [aviso] {os.path.basename(caminho)}: duração ({duracao_total:.0f}s) "
              f"<= warm-up ({warmup_s}s). Usando todos os dados.")
    return it.metric_value.values


def carregar_serie_sucesso(caminho, bin_s=5):
    """
    Para o cenário 3: série temporal de taxa de sucesso ao longo do tempo,
    agrupada em janelas de bin_s segundos. Retorna (tempos_rel, taxas).
    """
    df = pd.read_csv(caminho)
    chk = df[df.metric_name == "checks"].copy()
    if chk.empty:
        # fallback: usa http_req_failed invertido
        chk = df[df.metric_name == "http_req_failed"].copy()
        chk["metric_value"] = 1 - chk["metric_value"]
    if chk.empty:
        return np.array([]), np.array([])
    t0 = chk.timestamp.min()
    chk["t_rel"] = chk.timestamp - t0
    chk["bin"] = (chk.t_rel // bin_s) * bin_s
    agrupado = chk.groupby("bin").metric_value.mean()
    return agrupado.index.values, agrupado.values * 100


def calcular_throughput(caminho, warmup_s=60):
    """Throughput = iterações bem-sucedidas / duração efetiva (req/s)."""
    df = pd.read_csv(caminho)
    it = df[df.metric_name == "iteration_duration"].copy()
    if it.empty:
        return 0.0
    t0 = it.timestamp.min()
    duracao_total = it.timestamp.max() - t0
    if duracao_total > warmup_s:
        it = it[it.timestamp >= t0 + warmup_s]
    if it.empty:
        return 0.0
    duracao = it.timestamp.max() - it.timestamp.min()
    return len(it) / duracao if duracao > 0 else 0.0


def taxa_sucesso(caminho):
    """Fração de requisições HTTP bem-sucedidas (1 - http_req_failed)."""
    df = pd.read_csv(caminho)
    f = df[df.metric_name == "http_req_failed"]
    if f.empty:
        return np.nan
    return (1 - f.metric_value.mean()) * 100


def consolidar():
    """
    Monta um DataFrame com uma linha por (cenario, versao, rep) contendo
    as estatísticas agregadas daquela execução.
    """
    linhas = []
    for caminho, cenario, versao, rep in descobrir_arquivos():
        lat = carregar_latencias(caminho)
        if len(lat) == 0:
            continue
        linhas.append({
            "cenario": cenario,
            "versao": versao,
            "rep": rep,
            "lat_media": np.mean(lat),
            "lat_p50": np.percentile(lat, 50),
            "lat_p95": np.percentile(lat, 95),
            "lat_p99": np.percentile(lat, 99),
            "throughput": calcular_throughput(caminho),
            "sucesso_pct": taxa_sucesso(caminho),
            "n_amostras": len(lat),
        })
    return pd.DataFrame(linhas)


def tabela_resumo(df):
    """Agrega as repetições: média e desvio-padrão de cada métrica."""
    if df.empty:
        print("AVISO: nenhum dado encontrado para resumir.")
        return pd.DataFrame()

    metricas = ["lat_media", "lat_p50", "lat_p95", "lat_p99", "throughput", "sucesso_pct"]
    agg = df.groupby(["cenario", "versao"])[metricas].agg(["mean", "std"])
    agg.columns = [f"{m}_{s}" for m, s in agg.columns]
    agg = agg.reset_index()

    caminho = os.path.join(OUTPUT_DIR, "tabela_resumo.csv")
    agg.to_csv(caminho, index=False, float_format="%.2f")
    print(f"[ok] Tabela resumo salva em {caminho}")

    # Imprime versão legível no console
    print("\n" + "=" * 70)
    print("RESUMO POR CENÁRIO E VERSÃO (média das repetições)")
    print("=" * 70)
    for _, r in agg.iterrows():
        print(f"\nCenário {int(r['cenario'])} | {r['versao'].upper()}")
        print(f"  Latência média: {r['lat_media_mean']:.1f} ms (±{r['lat_media_std']:.1f})")
        print(f"  P50: {r['lat_p50_mean']:.1f} ms | P95: {r['lat_p95_mean']:.1f} ms | P99: {r['lat_p99_mean']:.1f} ms")
        print(f"  Throughput: {r['throughput_mean']:.1f} req/s")
        print(f"  Taxa de sucesso: {r['sucesso_pct_mean']:.1f}%")
    return agg


def testes_hipotese(df):
    """
    Para cada cenário, compara REST vs MSG na latência média das repetições.
    Usa Shapiro-Wilk para normalidade e então t pareado ou Mann-Whitney.
    """
    linhas = ["TESTES DE HIPÓTESE — REST vs MSG (latência média por repetição)\n"]
    linhas.append("Nível de significância: alpha = 0,05\n")
    linhas.append("=" * 60 + "\n")

    for cenario in sorted(df.cenario.unique()):
        sub = df[df.cenario == cenario]
        rest = sub[sub.versao == "rest"].lat_media.values
        msg = sub[sub.versao == "msg"].lat_media.values

        linhas.append(f"\nCenário {cenario}:")
        if len(rest) < 3 or len(msg) < 3:
            linhas.append(f"  Dados insuficientes (REST={len(rest)}, MSG={len(msg)} reps).")
            linhas.append("  Necessário >= 3 repetições de cada versão.")
            continue

        # Normalidade
        _, p_rest = stats.shapiro(rest)
        _, p_msg = stats.shapiro(msg)
        normal = p_rest > 0.05 and p_msg > 0.05

        if normal:
            # t de Student (amostras independentes)
            stat, p = stats.ttest_ind(rest, msg)
            teste = "t de Student (independente)"
        else:
            stat, p = stats.mannwhitneyu(rest, msg, alternative="two-sided")
            teste = "Mann-Whitney U"

        linhas.append(f"  REST: média={rest.mean():.1f} ms (n={len(rest)})")
        linhas.append(f"  MSG:  média={msg.mean():.1f} ms (n={len(msg)})")
        linhas.append(f"  Normalidade (Shapiro): REST p={p_rest:.3f}, MSG p={p_msg:.3f} -> {'normal' if normal else 'não-normal'}")
        linhas.append(f"  Teste aplicado: {teste}")
        linhas.append(f"  Estatística={stat:.3f}, p-valor={p:.4f}")
        if p < 0.05:
            vencedor = "REST" if rest.mean() < msg.mean() else "MSG"
            linhas.append(f"  => Diferença SIGNIFICATIVA (p<0,05). Menor latência: {vencedor}")
        else:
            linhas.append(f"  => Diferença NÃO significativa (p>=0,05).")

    texto = "\n".join(linhas)
    caminho = os.path.join(OUTPUT_DIR, "testes_hipotese.txt")
    with open(caminho, "w") as f:
        f.write(texto)
    print(f"\n[ok] Testes de hipótese salvos em {caminho}")


def grafico_boxplot_latencia(cenario, titulo, nome_arquivo):
    """Boxplot de latência REST vs MSG para um cenário (usa dados brutos)."""
    dados = {"rest": [], "msg": []}
    for caminho, c, versao, rep in descobrir_arquivos():
        if c == cenario:
            dados[versao].extend(carregar_latencias(caminho))

    if not dados["rest"] and not dados["msg"]:
        return

    fig, ax = plt.subplots(figsize=(7, 5))
    caixas, rotulos, cores = [], [], []
    if dados["rest"]:
        caixas.append(dados["rest"]); rotulos.append("REST"); cores.append(COR_REST)
    if dados["msg"]:
        caixas.append(dados["msg"]); rotulos.append("Mensageria"); cores.append(COR_MSG)

    bp = ax.boxplot(caixas, labels=rotulos, patch_artist=True, showfliers=False)
    for patch, cor in zip(bp["boxes"], cores):
        patch.set_facecolor(cor)
        patch.set_alpha(0.6)

    ax.set_ylabel("Latência fim-a-fim (ms)")
    ax.set_title(titulo)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)
    fig.savefig(caminho, dpi=150)
    plt.close(fig)
    print(f"[ok] Gráfico salvo em {caminho}")


def grafico_resiliencia(nome_arquivo="grafico_cenario3_resiliencia.png"):
    """Série temporal de taxa de sucesso no cenário 3 (com janela de falha)."""
    fig, ax = plt.subplots(figsize=(9, 5))
    plotou = False
    for versao, cor, rotulo in [("rest", COR_REST, "REST"), ("msg", COR_MSG, "Mensageria")]:
        # pega a primeira repetição disponível para ilustrar a série
        for caminho, c, v, rep in descobrir_arquivos():
            if c == 3 and v == versao:
                tempos, taxas = carregar_serie_sucesso(caminho)
                if len(tempos):
                    ax.plot(tempos, taxas, label=rotulo, color=cor, linewidth=2)
                    plotou = True
                break

    if not plotou:
        plt.close(fig)
        return

    # janela de falha: 120s a 150s (conforme run-all.sh)
    ax.axvspan(120, 150, color="gray", alpha=0.2, label="Estoque fora do ar")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Taxa de sucesso (%)")
    ax.set_title("Cenário 3 — Resiliência sob falha do serviço de Estoque")
    ax.set_ylim(-5, 105)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)
    fig.savefig(caminho, dpi=150)
    plt.close(fig)
    print(f"[ok] Gráfico salvo em {caminho}")


def grafico_comparativo(df, nome_arquivo="grafico_comparativo_latencia.png"):
    """Barras de latência média por cenário, REST vs MSG lado a lado."""
    if df.empty:
        return
    resumo = df.groupby(["cenario", "versao"]).lat_media.mean().unstack("versao")
    if resumo.empty:
        return

    fig, ax = plt.subplots(figsize=(9, 5))
    cenarios = resumo.index.values
    x = np.arange(len(cenarios))
    largura = 0.35

    if "rest" in resumo.columns:
        ax.bar(x - largura/2, resumo["rest"].values, largura, label="REST", color=COR_REST, alpha=0.8)
    if "msg" in resumo.columns:
        ax.bar(x + largura/2, resumo["msg"].values, largura, label="Mensageria", color=COR_MSG, alpha=0.8)

    ax.set_xlabel("Cenário")
    ax.set_ylabel("Latência média (ms)")
    ax.set_title("Latência média por cenário")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Cenário {int(c)}" for c in cenarios])
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)
    fig.savefig(caminho, dpi=150)
    plt.close(fig)
    print(f"[ok] Gráfico salvo em {caminho}")


def main():
    print("Lendo CSVs de:", os.path.abspath(RESULTS_DIR))
    arquivos = descobrir_arquivos()
    if not arquivos:
        print("\nNenhum CSV no padrão 'cenario<N>_<versao>_rep<R>.csv' encontrado.")
        print("Rode os benchmarks primeiro (benchmarks/run-all.sh).")
        return

    print(f"Encontrados {len(arquivos)} arquivos.\n")

    df = consolidar()
    agg = tabela_resumo(df)
    if not df.empty:
        testes_hipotese(df)

        # Gráficos por cenário (só gera os que têm dados)
        cenarios_presentes = sorted(df.cenario.unique())
        if 1 in cenarios_presentes:
            grafico_boxplot_latencia(1, "Cenário 1 — Latência sob carga constante",
                                     "grafico_cenario1_latencia.png")
        if 4 in cenarios_presentes:
            grafico_boxplot_latencia(4, "Cenário 4 — Latência de consulta",
                                     "grafico_cenario4_latencia.png")
        if 3 in cenarios_presentes:
            grafico_resiliencia()
        grafico_comparativo(df)

    print("\nConcluído. Arquivos em:", os.path.abspath(OUTPUT_DIR))


if __name__ == "__main__":
    main()
