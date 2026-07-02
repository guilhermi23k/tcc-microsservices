#!/usr/bin/env python3
"""
Análise dos resultados dos benchmarks REST vs Mensageria.
<<<<<<< Updated upstream

Lê os CSVs gerados pelo k6 (../benchmarks/results/) e produz tabelas
estatísticas e gráficos para os capítulos 5 e 6 do TCC.

Padrão de nomes esperado: cenario<N>_<versao>_rep<R>.csv
=======
Versão 2 — gráficos profissionais para TCC.
>>>>>>> Stashed changes
"""

import os
import re
import glob
import warnings

import numpy as np
import pandas as pd
import matplotlib
<<<<<<< Updated upstream
matplotlib.use("Agg")  # backend sem display (gera arquivos)
import matplotlib.pyplot as plt
=======
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
>>>>>>> Stashed changes
from scipy import stats

warnings.filterwarnings("ignore")

<<<<<<< Updated upstream
=======
# ============================================================
# CONFIGURAÇÃO VISUAL
# ============================================================
# Paleta acessível (funciona em P&B e para daltônicos)
COR_REST = "#3274A1"    # azul aço
COR_MSG  = "#E1812C"    # laranja queimado
COR_FALHA = "#CCCCCC"   # cinza claro (faixa de falha)

# Estilo global
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})

>>>>>>> Stashed changes
# Caminhos
AQUI = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(AQUI, "..", "benchmarks", "results")
OUTPUT_DIR = os.path.join(AQUI, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

<<<<<<< Updated upstream
# Cores fixas por versão (consistência visual nos gráficos)
COR_REST = "#2563eb"  # azul
COR_MSG = "#dc2626"   # vermelho

PADRAO = re.compile(r"cenario(\d+)_(rest|msg)_rep(\d+)\.csv$")


def descobrir_arquivos():
    """Retorna lista de (caminho, cenario, versao, rep) dos CSVs encontrados."""
=======
PADRAO = re.compile(r"cenario(\d+)_(rest|msg)_rep(\d+)\.csv$")

# ============================================================
# FUNÇÕES DE LEITURA
# ============================================================

def descobrir_arquivos():
>>>>>>> Stashed changes
    arquivos = []
    for caminho in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.csv"))):
        m = PADRAO.search(os.path.basename(caminho))
        if m:
            arquivos.append((caminho, int(m.group(1)), m.group(2), int(m.group(3))))
    return arquivos


def carregar_latencias(caminho, warmup_s=60):
<<<<<<< Updated upstream
    """
    Extrai as latências fim-a-fim (iteration_duration) de um CSV do k6,
    descartando o período de warm-up inicial.
    Retorna um array numpy de latências em ms.
    """
=======
>>>>>>> Stashed changes
    df = pd.read_csv(caminho)
    it = df[df.metric_name == "iteration_duration"].copy()
    if it.empty:
        return np.array([])
<<<<<<< Updated upstream
    # descarta warm-up: primeiros warmup_s segundos
=======
>>>>>>> Stashed changes
    t0 = it.timestamp.min()
    duracao_total = it.timestamp.max() - t0
    if duracao_total > warmup_s:
        it = it[it.timestamp >= t0 + warmup_s]
    else:
<<<<<<< Updated upstream
        # Execução mais curta que o warm-up (ex.: teste rápido).
        # Usa todos os dados em vez de descartar tudo.
        print(f"  [aviso] {os.path.basename(caminho)}: duração ({duracao_total:.0f}s) "
              f"<= warm-up ({warmup_s}s). Usando todos os dados.")
=======
        pass  # execução curta, usa tudo
>>>>>>> Stashed changes
    return it.metric_value.values


def carregar_serie_sucesso(caminho, bin_s=5):
    df = pd.read_csv(caminho)
    chk = df[df.metric_name == "checks"].copy()
    if chk.empty:
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
<<<<<<< Updated upstream
    """Throughput = iterações bem-sucedidas / duração efetiva (req/s)."""
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
    """Fração de requisições HTTP bem-sucedidas (1 - http_req_failed)."""
=======
>>>>>>> Stashed changes
    df = pd.read_csv(caminho)
    f = df[df.metric_name == "http_req_failed"]
    if f.empty:
        return np.nan
    return (1 - f.metric_value.mean()) * 100


<<<<<<< Updated upstream
def consolidar():
    """
    Monta um DataFrame com uma linha por (cenario, versao, rep) contendo
    as estatísticas agregadas daquela execução.
    """
=======
def _remover_outliers_iqr(valores):
    arr = np.asarray(valores, dtype=float)
    if len(arr) == 0:
        return arr, 0, 0.0
    q1, q3 = np.percentile(arr, [25, 75])
    iqr = q3 - q1
    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr
    mask = (arr >= lim_inf) & (arr <= lim_sup)
    limpos = arr[mask]
    n_out = len(arr) - len(limpos)
    pct = 100.0 * n_out / len(arr) if len(arr) else 0.0
    return limpos, n_out, pct


# ============================================================
# CONSOLIDAÇÃO
# ============================================================

def consolidar():
>>>>>>> Stashed changes
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
    if df.empty:
        print("AVISO: nenhum dado encontrado para resumir.")
        return pd.DataFrame()
    metricas = ["lat_media", "lat_p50", "lat_p95", "lat_p99", "throughput", "sucesso_pct"]
    agg = df.groupby(["cenario", "versao"])[metricas].agg(["mean", "std"])
    agg.columns = [f"{m}_{s}" for m, s in agg.columns]
    agg = agg.reset_index()
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    caminho = os.path.join(OUTPUT_DIR, "tabela_resumo.csv")
    agg.to_csv(caminho, index=False, float_format="%.2f")
    print(f"[ok] Tabela resumo salva em {caminho}")

<<<<<<< Updated upstream
    # Imprime versão legível no console
=======
>>>>>>> Stashed changes
    print("\n" + "=" * 70)
    print("RESUMO POR CENÁRIO E VERSÃO (média das repetições)")
    print("=" * 70)
    for _, r in agg.iterrows():
<<<<<<< Updated upstream
        print(f"\nCenário {int(r['cenario'])} | {r['versao'].upper()}")
=======
        label = "REST" if r["versao"] == "rest" else "MSG"
        print(f"\nCenário {int(r['cenario'])} | {label}")
>>>>>>> Stashed changes
        print(f"  Latência média: {r['lat_media_mean']:.1f} ms (±{r['lat_media_std']:.1f})")
        print(f"  P50: {r['lat_p50_mean']:.1f} ms | P95: {r['lat_p95_mean']:.1f} ms | P99: {r['lat_p99_mean']:.1f} ms")
        print(f"  Throughput: {r['throughput_mean']:.1f} req/s")
        print(f"  Taxa de sucesso: {r['sucesso_pct_mean']:.1f}%")
    return agg


def testes_hipotese(df):
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
            stat, p = stats.ttest_ind(rest, msg)
            teste = "t de Student (independente)"
        else:
            stat, p = stats.mannwhitneyu(rest, msg, alternative="two-sided")
            teste = "Mann-Whitney U"
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    texto = "\n".join(linhas)
    caminho = os.path.join(OUTPUT_DIR, "testes_hipotese.txt")
    with open(caminho, "w") as f:
        f.write(texto)
    print(f"\n[ok] Testes de hipótese salvos em {caminho}")


<<<<<<< Updated upstream
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
=======
# ============================================================
# GRÁFICOS PROFISSIONAIS
# ============================================================

def grafico_violino_latencia(cenario, titulo, nome_arquivo):
    """
    Painel triplo: boxplot comparativo + violino REST + violino MSG,
    cada um com escala própria pra legibilidade máxima.
    """
    brutos = {"rest": [], "msg": []}
    for caminho, c, versao, rep in descobrir_arquivos():
        if c == cenario:
            brutos[versao].extend(carregar_latencias(caminho))

    if not brutos["rest"] and not brutos["msg"]:
        return

    # Prepara dados limpos
    dados = {}
    for versao in ["rest", "msg"]:
        if brutos[versao]:
            limpos, n_out, pct = _remover_outliers_iqr(brutos[versao])
            med = np.median(limpos)
            q1 = np.percentile(limpos, 25)
            q3 = np.percentile(limpos, 75)
            dados[versao] = {"limpos": limpos, "n_out": n_out, "pct": pct,
                             "med": med, "q1": q1, "q3": q3}

    if len(dados) < 2:
        return

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 5.5),
                                          gridspec_kw={"width_ratios": [1.2, 1, 1]})

    # === PAINEL 1: Boxplot comparativo ===
    box_data = [dados["rest"]["limpos"], dados["msg"]["limpos"]]
    bp = ax1.boxplot(box_data, tick_labels=["REST", "Mensageria"],
                      patch_artist=True, showfliers=False, widths=0.5,
                      medianprops=dict(color="white", linewidth=2))
    bp["boxes"][0].set_facecolor(COR_REST); bp["boxes"][0].set_alpha(0.8)
    bp["boxes"][1].set_facecolor(COR_MSG);  bp["boxes"][1].set_alpha(0.8)

    for i, (versao, cor) in enumerate([("rest", COR_REST), ("msg", COR_MSG)], 1):
        med = dados[versao]["med"]
        ax1.annotate(f"{med:.1f} ms", xy=(i, med), xytext=(0.4, 0),
                    textcoords="offset fontsize", fontsize=9.5, weight="bold",
                    color="white", va="center",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor=cor,
                              alpha=0.9, edgecolor="none"))

    ax1.set_ylabel("Latência fim a fim (ms)")
    ax1.set_title("Comparativo", weight="bold")
    ax1.grid(axis="y", alpha=0.2, linestyle="--")
    ax1.set_axisbelow(True)

    # === PAINEL 2: Violino REST ===
    d = dados["rest"]
    vp2 = ax2.violinplot([d["limpos"]], positions=[1], showmedians=False, showextrema=False)
    vp2["bodies"][0].set_facecolor(COR_REST)
    vp2["bodies"][0].set_alpha(0.45)
    vp2["bodies"][0].set_edgecolor(COR_REST)
    vp2["bodies"][0].set_linewidth(1.2)

    ax2.hlines(d["med"], 0.85, 1.15, color=COR_REST, linewidth=2.5, zorder=5)
    ax2.hlines([d["q1"], d["q3"]], 0.92, 1.08, color=COR_REST, linewidth=1, alpha=0.6, zorder=5)
    ax2.vlines(1, d["q1"], d["q3"], color=COR_REST, linewidth=1, alpha=0.6, zorder=4)

    ax2.annotate(f"Mediana: {d['med']:.1f} ms\nQ1: {d['q1']:.1f} \u00b7 Q3: {d['q3']:.1f}",
                 xy=(1.18, d["med"]), fontsize=9, color=COR_REST, va="center",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                           edgecolor=COR_REST, alpha=0.85, linewidth=0.8))
    ax2.annotate(f"{d['n_out']} outliers removidos ({d['pct']:.1f}%)",
                 xy=(0.5, 0.97), xycoords="axes fraction", ha="center",
                 fontsize=8.5, color="#777")

    ax2.set_xticks([1])
    ax2.set_xticklabels(["REST"], fontsize=12, weight="bold", color=COR_REST)
    ax2.set_title("Distribuição REST", weight="bold", color=COR_REST)
    ax2.set_ylabel("Latência (ms)")
    ax2.grid(axis="y", alpha=0.2, linestyle="--")
    ax2.set_axisbelow(True)

    # === PAINEL 3: Violino MSG ===
    d = dados["msg"]
    vp3 = ax3.violinplot([d["limpos"]], positions=[1], showmedians=False, showextrema=False)
    vp3["bodies"][0].set_facecolor(COR_MSG)
    vp3["bodies"][0].set_alpha(0.45)
    vp3["bodies"][0].set_edgecolor(COR_MSG)
    vp3["bodies"][0].set_linewidth(1.2)

    ax3.hlines(d["med"], 0.85, 1.15, color=COR_MSG, linewidth=2.5, zorder=5)
    ax3.hlines([d["q1"], d["q3"]], 0.92, 1.08, color=COR_MSG, linewidth=1, alpha=0.6, zorder=5)
    ax3.vlines(1, d["q1"], d["q3"], color=COR_MSG, linewidth=1, alpha=0.6, zorder=4)

    ax3.annotate(f"Mediana: {d['med']:.1f} ms\nQ1: {d['q1']:.1f} \u00b7 Q3: {d['q3']:.1f}",
                 xy=(1.18, d["med"]), fontsize=9, color=COR_MSG, va="center",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                           edgecolor=COR_MSG, alpha=0.85, linewidth=0.8))
    ax3.annotate(f"{d['n_out']} outliers removidos ({d['pct']:.1f}%)",
                 xy=(0.5, 0.97), xycoords="axes fraction", ha="center",
                 fontsize=8.5, color="#777")

    ax3.set_xticks([1])
    ax3.set_xticklabels(["Mensageria"], fontsize=12, weight="bold", color=COR_MSG)
    ax3.set_title("Distribuição Mensageria", weight="bold", color=COR_MSG)
    ax3.set_ylabel("Latência (ms)")
    ax3.grid(axis="y", alpha=0.2, linestyle="--")
    ax3.set_axisbelow(True)

    fig.suptitle(titulo, fontsize=14, weight="bold", y=1.02)
    fig.tight_layout()
    caminho_out = os.path.join(OUTPUT_DIR, nome_arquivo)
    fig.savefig(caminho_out)
    plt.close(fig)
    print(f"[ok] {nome_arquivo}")


def grafico_resiliencia(nome_arquivo="grafico_cenario3_resiliencia.png"):
    """
    Série temporal de resiliência com:
    - Faixa de falha sombreada
    - Anotações de eventos
    - Estilo profissional
    """
    fig, ax = plt.subplots(figsize=(10, 5.5))
    plotou = False

    estilos = [
        ("rest", COR_REST, "REST", "-", 2.5),
        ("msg", COR_MSG, "Mensageria", "-", 2.5),
    ]
    for versao, cor, rotulo, ls, lw in estilos:
>>>>>>> Stashed changes
        for caminho, c, v, rep in descobrir_arquivos():
            if c == 3 and v == versao:
                tempos, taxas = carregar_serie_sucesso(caminho)
                if len(tempos):
<<<<<<< Updated upstream
                    ax.plot(tempos, taxas, label=rotulo, color=cor, linewidth=2)
=======
                    ax.plot(tempos, taxas, label=rotulo, color=cor,
                            linewidth=lw, linestyle=ls, zorder=3)
>>>>>>> Stashed changes
                    plotou = True
                break

    if not plotou:
        plt.close(fig)
        return

<<<<<<< Updated upstream
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
=======
    # Faixa de falha
    ax.axvspan(120, 150, color=COR_FALHA, alpha=0.4, zorder=1,
               label="Estoque fora do ar")

    # Anotações de eventos
    ax.annotate("Estoque\nderrubado", xy=(120, 50), fontsize=9,
                ha="center", color="#555", style="italic")
    ax.annotate("Estoque\nrestaurado", xy=(150, 50), fontsize=9,
                ha="center", color="#555", style="italic")

    # Anotação do comportamento
    ax.annotate("REST: falha em cascata\n(0% de sucesso)", xy=(135, 8),
                fontsize=9, ha="center", color=COR_REST, weight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=COR_REST, alpha=0.8))
    ax.annotate("Mensageria: 100%\n(mensagens retidas na fila)", xy=(250, 85),
                fontsize=9, ha="center", color=COR_MSG, weight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=COR_MSG, alpha=0.8))

    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Taxa de sucesso (%)")
    ax.set_title("Cenário 3 — Resiliência sob falha do serviço de Estoque", pad=15)
    ax.set_ylim(-5, 110)
    ax.set_xlim(left=0)
    ax.legend(loc="lower left", framealpha=0.9)
    ax.grid(alpha=0.2, linestyle="--")
    ax.set_axisbelow(True)
    fig.tight_layout()
    caminho_out = os.path.join(OUTPUT_DIR, nome_arquivo)
    fig.savefig(caminho_out)
    plt.close(fig)
    print(f"[ok] {nome_arquivo}")


def grafico_comparativo_barras(df, nome_arquivo="grafico_comparativo_latencia.png"):
    """
    Barras de latência MEDIANA por cenário (em vez de média, pra não inflar
    com timeouts), com valores anotados sobre cada barra.
    """
    if df.empty:
        return
    resumo = df.groupby(["cenario", "versao"]).lat_p50.mean().unstack("versao")
    if resumo.empty:
        return

    fig, ax = plt.subplots(figsize=(10, 5.5))
    cenarios = resumo.index.values
    x = np.arange(len(cenarios))
    largura = 0.32
    nomes_cenarios = {
        1: "Carga\nconstante",
        2: "Carga\ncrescente",
        3: "Falha\ninjetada",
        4: "Consulta",
    }

    for i, (versao, cor, rotulo) in enumerate([
        ("rest", COR_REST, "REST"),
        ("msg", COR_MSG, "Mensageria")
    ]):
        if versao in resumo.columns:
            vals = resumo[versao].values
            offset = -largura/2 + i * largura
            bars = ax.bar(x + offset, vals, largura, label=rotulo,
                         color=cor, alpha=0.85, edgecolor="white", linewidth=0.8)
            # Anota valores sobre cada barra
            for bar, val in zip(bars, vals):
                if val > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                            f"{val:.1f}",
                            ha="center", va="bottom", fontsize=9, weight="bold", color=cor)

    ax.set_xlabel("Cenário")
    ax.set_ylabel("Latência mediana (ms)")
    ax.set_title("Comparativo de latência mediana por cenário", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([nomes_cenarios.get(int(c), f"Cen. {int(c)}") for c in cenarios])
    ax.legend(framealpha=0.9)
    ax.grid(axis="y", alpha=0.2, linestyle="--")
    ax.set_axisbelow(True)
    fig.tight_layout()
    caminho_out = os.path.join(OUTPUT_DIR, nome_arquivo)
    fig.savefig(caminho_out)
    plt.close(fig)
    print(f"[ok] {nome_arquivo}")


def grafico_taxa_sucesso(df, nome_arquivo="grafico_taxa_sucesso.png"):
    """
    Barras horizontais de taxa de sucesso por cenário/versão.
    Destaca o cenário 3 onde REST falha.
    """
    if df.empty:
        return
    resumo = df.groupby(["cenario", "versao"]).sucesso_pct.mean().unstack("versao")
>>>>>>> Stashed changes
    if resumo.empty:
        return

    fig, ax = plt.subplots(figsize=(9, 5))
    cenarios = resumo.index.values
<<<<<<< Updated upstream
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


=======
    y = np.arange(len(cenarios))
    altura = 0.32
    nomes_cenarios = {
        1: "Cen. 1 — Carga constante",
        2: "Cen. 2 — Carga crescente",
        3: "Cen. 3 — Falha injetada",
        4: "Cen. 4 — Consulta",
    }

    for i, (versao, cor, rotulo) in enumerate([
        ("rest", COR_REST, "REST"),
        ("msg", COR_MSG, "Mensageria")
    ]):
        if versao in resumo.columns:
            vals = resumo[versao].values
            offset = -altura/2 + i * altura
            bars = ax.barh(y + offset, vals, altura, label=rotulo,
                          color=cor, alpha=0.85, edgecolor="white", linewidth=0.8)
            for bar, val in zip(bars, vals):
                ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                        f"{val:.1f}%",
                        ha="left", va="center", fontsize=9, weight="bold", color=cor)

    ax.set_yticks(y)
    ax.set_yticklabels([nomes_cenarios.get(int(c), f"Cenário {int(c)}") for c in cenarios])
    ax.set_xlabel("Taxa de sucesso (%)")
    ax.set_title("Taxa de sucesso por cenário e versão", pad=15)
    ax.set_xlim(0, 115)
    ax.legend(loc="lower right", framealpha=0.9)
    ax.grid(axis="x", alpha=0.2, linestyle="--")
    ax.set_axisbelow(True)
    # Linha de referência em 100%
    ax.axvline(100, color="#aaa", linewidth=0.8, linestyle="--", zorder=1)
    fig.tight_layout()
    caminho_out = os.path.join(OUTPUT_DIR, nome_arquivo)
    fig.savefig(caminho_out)
    plt.close(fig)
    print(f"[ok] {nome_arquivo}")


def grafico_tabela_resumo(df, nome_arquivo="tabela_visual.png"):
    """
    Tabela visual com cores por versão e texto completo.
    """
    if df.empty:
        return

    resumo = df.groupby(["cenario", "versao"]).agg({
        "lat_p50": "mean",
        "lat_p95": "mean",
        "throughput": "mean",
        "sucesso_pct": "mean"
    }).reset_index()

    nomes = {1: "Carga constante", 2: "Carga crescente", 3: "Falha injetada", 4: "Consulta"}

    linhas = []
    for _, r in resumo.iterrows():
        label = "REST" if r.versao == "rest" else "MSG"
        p95_fmt = f"{r.lat_p95:,.1f}".replace(",", ".")
        linhas.append([
            f"Cen. {int(r.cenario)} \u2014 {nomes.get(int(r.cenario), '')}",
            label,
            f"{r.lat_p50:.1f}",
            p95_fmt,
            f"{r.throughput:.1f}",
            f"{r.sucesso_pct:.1f}%"
        ])

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis("off")
    colunas = ["Cenário", "Versão", "P50 (ms)", "P95 (ms)", "Vazão\n(req/s)", "Sucesso"]
    tabela = ax.table(
        cellText=linhas,
        colLabels=colunas,
        cellLoc="center",
        loc="center",
        colWidths=[0.28, 0.10, 0.12, 0.14, 0.12, 0.12],
    )
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10.5)
    tabela.scale(1, 1.7)

    COR_REST_BG = "#E8F0F8"
    COR_MSG_BG  = "#FDF0E6"

    for j in range(len(colunas)):
        tabela[0, j].set_facecolor("#2C3E50")
        tabela[0, j].set_text_props(color="white", weight="bold", fontsize=11)
        tabela[0, j].set_edgecolor("#1a252f")

    for i, linha in enumerate(linhas, start=1):
        is_msg = linha[1] == "MSG"
        cor_bg = COR_MSG_BG if is_msg else COR_REST_BG
        cor_txt = COR_MSG if is_msg else COR_REST

        for j in range(len(colunas)):
            tabela[i, j].set_facecolor(cor_bg)
            tabela[i, j].set_edgecolor("#DDD")
            tabela[i, j].set_text_props(fontsize=10.5)

        tabela[i, 1].set_text_props(color=cor_txt, weight="bold", fontsize=11)

        suc_val = float(linha[5].replace("%", "").replace(",", "."))
        if suc_val < 99:
            tabela[i, 5].set_text_props(color="#CC0000", weight="bold")

    ax.set_title("Síntese dos resultados experimentais", pad=25, fontsize=14, weight="bold")
    fig.tight_layout()
    caminho_out = os.path.join(OUTPUT_DIR, nome_arquivo)
    fig.savefig(caminho_out)
    plt.close(fig)
    print(f"[ok] {nome_arquivo}")


def grafico_percentis(df, nome_arquivo="grafico_percentis.png"):
    """
    Gráfico de barras agrupadas mostrando P50, P95, P99 por cenário,
    REST vs MSG lado a lado.
    """
    if df.empty:
        return

    cenarios_presentes = sorted(df.cenario.unique())
    fig, axes = plt.subplots(1, len(cenarios_presentes), figsize=(4 * len(cenarios_presentes), 5),
                              sharey=False)
    if len(cenarios_presentes) == 1:
        axes = [axes]

    nomes = {1: "Carga constante", 2: "Carga crescente", 3: "Falha injetada", 4: "Consulta"}

    for ax, cenario in zip(axes, cenarios_presentes):
        sub = df[df.cenario == cenario]
        metricas = ["lat_p50", "lat_p95", "lat_p99"]
        rotulos = ["P50", "P95", "P99"]
        x = np.arange(len(metricas))
        largura = 0.35

        for i, (versao, cor, rotulo) in enumerate([
            ("rest", COR_REST, "REST"),
            ("msg", COR_MSG, "Mensageria")
        ]):
            vals_sub = sub[sub.versao == versao]
            if vals_sub.empty:
                continue
            vals = [vals_sub[m].mean() for m in metricas]
            offset = -largura/2 + i * largura
            bars = ax.bar(x + offset, vals, largura, label=rotulo,
                         color=cor, alpha=0.85, edgecolor="white")
            for bar, val in zip(bars, vals):
                if val < 1000:
                    txt = f"{val:.1f}"
                else:
                    txt = f"{val:.0f}"
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                        txt, ha="center", va="bottom", fontsize=7.5, color=cor)

        ax.set_xticks(x)
        ax.set_xticklabels(rotulos)
        ax.set_title(f"Cen. {cenario}\n{nomes.get(cenario, '')}", fontsize=10)
        ax.grid(axis="y", alpha=0.2, linestyle="--")
        ax.set_axisbelow(True)
        if cenario == cenarios_presentes[0]:
            ax.set_ylabel("Latência (ms)")

    axes[-1].legend(loc="upper right", fontsize=9)
    fig.suptitle("Percentis de latência por cenário", fontsize=13, weight="bold", y=1.02)
    fig.tight_layout()
    caminho_out = os.path.join(OUTPUT_DIR, nome_arquivo)
    fig.savefig(caminho_out)
    plt.close(fig)
    print(f"[ok] {nome_arquivo}")


# ============================================================
# MAIN
# ============================================================

def grafico_cenario2_latencia_por_carga(nome_arquivo="grafico_cenario2_latencia_por_carga.png"):
    """
    Painel triplo pro cenário 2:
    - Topo: mediana com dois eixos Y independentes (REST esq, MSG dir)
    - Inferior esq: P95 REST em zoom (mostra estabilidade)
    - Inferior dir: P95 MSG (mostra joelho de saturação)
    """
    BIN_S = 15

    def serie(caminho, warmup_s=60):
        df = pd.read_csv(caminho)
        it = df[df.metric_name == "iteration_duration"].copy()
        if it.empty:
            return None
        t0 = it.timestamp.min()
        it["t_rel"] = it.timestamp - t0
        if it.t_rel.max() > warmup_s:
            it = it[it.t_rel >= warmup_s]
            it["t_rel"] = it["t_rel"] - warmup_s
        it["bin"] = (it.t_rel // BIN_S) * BIN_S
        agg = it.groupby("bin").agg(
            mediana=("metric_value", "median"),
            p95=("metric_value", lambda x: x.quantile(0.95)),
            n=("metric_value", "count")
        )
        agg["taxa"] = agg["n"] / BIN_S
        return agg.sort_values("taxa")

    dados = {}
    for caminho, c, versao, rep in descobrir_arquivos():
        if c == 2 and versao not in dados:
            s = serie(caminho)
            if s is not None:
                dados[versao] = s
        if len(dados) == 2:
            break

    if not dados:
        return

    rest = dados.get("rest")
    msg  = dados.get("msg")

    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 2, hspace=0.45, wspace=0.35)
    ax_top = fig.add_subplot(gs[0, :])
    ax_bl  = fig.add_subplot(gs[1, 0])
    ax_br  = fig.add_subplot(gs[1, 1])

    # --- Topo: mediana com dois eixos Y ---
    ax_r = ax_top
    ax_m = ax_top.twinx()
    linhas = []
    if rest is not None:
        l1, = ax_r.plot(rest["taxa"], rest["mediana"], color=COR_REST, linewidth=2,
                        marker="o", markersize=4, label="REST (eixo esq.)")
        linhas.append(l1)
    if msg is not None:
        l2, = ax_m.plot(msg["taxa"], msg["mediana"], color=COR_MSG, linewidth=2,
                        marker="s", markersize=4, label="Mensageria (eixo dir.)")
        linhas.append(l2)

    ax_r.set_ylabel("Latência mediana REST (ms)", color=COR_REST)
    ax_r.tick_params(axis="y", labelcolor=COR_REST)
    ax_r.set_ylim(8, 22)
    ax_m.set_ylabel("Latência mediana MSG (ms)", color=COR_MSG)
    ax_m.tick_params(axis="y", labelcolor=COR_MSG)
    ax_m.set_ylim(100, 118)
    ax_r.set_xlabel("Taxa de requisições (req/s)")
    ax_r.set_title("Latência mediana por taxa de requisições\n(escalas independentes)", weight="bold")
    ax_r.grid(alpha=0.2, linestyle="--")
    ax_r.set_axisbelow(True)
    ax_r.legend(linhas, [l.get_label() for l in linhas], loc="upper right", framealpha=0.9)

    if rest is not None:
        ax_r.annotate("REST: estável\n(sem saturação)", xy=(85, 10.6),
                      fontsize=9, color=COR_REST, ha="center",
                      bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                                edgecolor=COR_REST, alpha=0.85))
    if msg is not None:
        ax_m.annotate("MSG: estável\nna mediana", xy=(85, 110.5),
                      fontsize=9, color=COR_MSG, ha="center",
                      bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                                edgecolor=COR_MSG, alpha=0.85))

    # --- Inferior esq: P95 REST ---
    if rest is not None:
        ax_bl.plot(rest["taxa"], rest["p95"], color=COR_REST, linewidth=2,
                   marker="o", markersize=4)
        ax_bl.set_ylim(0, 35)
        ax_bl.annotate("P95 < 20ms\nem toda a faixa", xy=(65, 12),
                       fontsize=9, color=COR_REST, ha="center",
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                                 edgecolor=COR_REST, alpha=0.85))
    ax_bl.set_xlabel("Taxa de requisições (req/s)")
    ax_bl.set_ylabel("Latência P95 (ms)")
    ax_bl.set_title("P95 — REST\n(sem saturação até ~97 req/s)", weight="bold", color=COR_REST)
    ax_bl.grid(alpha=0.2, linestyle="--")
    ax_bl.set_axisbelow(True)

    # --- Inferior dir: P95 MSG ---
    if msg is not None:
        ax_br.plot(msg["taxa"], msg["p95"], color=COR_MSG, linewidth=2,
                   marker="s", markersize=4, linestyle="--")
        ax_br.axhline(5000, color="gray", linewidth=0.8, linestyle=":", alpha=0.7)
        ax_br.annotate("Limite do polling (5 s)", xy=(msg["taxa"].min(), 5000),
                       xytext=(0, 6), textcoords="offset points",
                       fontsize=8, color="gray", style="italic")
        sat = msg[msg["p95"] > 500]
        if not sat.empty:
            tx = sat.iloc[0]["taxa"]
            py = sat.iloc[0]["p95"]
            # Posiciona a anotação abaixo do joelho, dentro da escala
            ax_br.annotate(f"Joelho: ~{tx:.0f} req/s\n(fila começa\na acumular)",
                           xy=(tx, py), xytext=(tx + 20, 2500),
                           fontsize=9, color=COR_MSG,
                           arrowprops=dict(arrowstyle="->", color=COR_MSG, lw=1.2),
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                                     edgecolor=COR_MSG, alpha=0.85))
    ax_br.set_xlabel("Taxa de requisições (req/s)")
    ax_br.set_ylabel("Latência P95 (ms)")
    ax_br.set_title("P95 — Mensageria\n(satura a ~32 req/s)", weight="bold", color=COR_MSG)
    ax_br.grid(alpha=0.2, linestyle="--")
    ax_br.set_axisbelow(True)

    fig.suptitle("Cenário 2 — Comportamento sob carga crescente",
                 fontsize=14, weight="bold", y=1.01)
    fig.savefig(os.path.join(OUTPUT_DIR, nome_arquivo))
    plt.close(fig)
    print(f"[ok] {nome_arquivo}")


def main():
    print("Lendo CSVs de:", os.path.abspath(RESULTS_DIR))
    arquivos = descobrir_arquivos()
    if not arquivos:
<<<<<<< Updated upstream
        print("\nNenhum CSV no padrão 'cenario<N>_<versao>_rep<R>.csv' encontrado.")
        print("Rode os benchmarks primeiro (benchmarks/run-all.sh).")
=======
        print("\nNenhum CSV encontrado.")
>>>>>>> Stashed changes
        return

    print(f"Encontrados {len(arquivos)} arquivos.\n")

    df = consolidar()
    agg = tabela_resumo(df)
<<<<<<< Updated upstream
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
=======
    if df.empty:
        return

    testes_hipotese(df)

    # Gráficos
    cenarios_presentes = sorted(df.cenario.unique())

    print("\nGerando gráficos profissionais...\n")

    if 1 in cenarios_presentes:
        grafico_violino_latencia(1, "Cenário 1 — Latência sob carga constante",
                                 "grafico_cenario1_latencia.png")
    if 2 in cenarios_presentes:
        grafico_violino_latencia(2, "Cenário 2 — Latência sob carga crescente",
                                 "grafico_cenario2_latencia.png")
        grafico_cenario2_latencia_por_carga()
    if 4 in cenarios_presentes:
        grafico_violino_latencia(4, "Cenário 4 — Latência de consulta",
                                 "grafico_cenario4_latencia.png")
    if 3 in cenarios_presentes:
        grafico_resiliencia()

    grafico_comparativo_barras(df)
    grafico_taxa_sucesso(df)
    grafico_tabela_resumo(df)
    grafico_percentis(df)

    print(f"\nConcluído. {len(os.listdir(OUTPUT_DIR))} arquivos em: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()
>>>>>>> Stashed changes
