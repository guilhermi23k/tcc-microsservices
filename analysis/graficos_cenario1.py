"""
graficos_cenario1.py
Gera gráficos melhorados para o cenário 1 (carga constante).
Uso: python3 graficos_cenario1.py
Espera CSVs em ../benchmarks/results/cenario1_{msg,rest}_rep*.csv
Salva PNGs em ./output/
"""

import glob
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

# ── Configuração ──────────────────────────────────────────────────────────────
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "../benchmarks/results")
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

COR_REST = "#2563eb"
COR_MSG  = "#dc2626"
ALPHA    = 0.05

# ── Leitura dos CSVs ──────────────────────────────────────────────────────────
def carregar_latencias(versao: str) -> list[np.ndarray]:
    """Retorna lista com array de latências fim-a-fim por repetição."""
    # A métrica que mede o tempo total da operação (polling incluso na MSG)
    # está em 'pedido_duration' se existir, senão usa http_req_duration
    padrao = os.path.join(RESULTS_DIR, f"cenario1_{versao}_rep*.csv")
    arquivos = sorted(glob.glob(padrao))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV encontrado para padrão: {padrao}")

    reps = []
    for arq in arquivos:
        df = pd.read_csv(arq)
        # Tenta métrica customizada de latência fim-a-fim (trend do k6)
        metrica = "pedido_duration" if "pedido_duration" in df["metric_name"].values else "http_req_duration"
        vals = df[df["metric_name"] == metrica]["metric_value"].dropna().values
        reps.append(vals)
    return reps


def remover_outliers_iqr(arr: np.ndarray):
    q1, q3 = np.percentile(arr, 25), np.percentile(arr, 75)
    iqr = q3 - q1
    mask = (arr >= q1 - 1.5 * iqr) & (arr <= q3 + 1.5 * iqr)
    return arr[mask], int((~mask).sum())


def percentis_por_rep(reps: list[np.ndarray]):
    """Retorna dict com arrays de p50, p95, p99, mean por rep."""
    p50  = [np.percentile(r, 50)  for r in reps]
    p95  = [np.percentile(r, 95)  for r in reps]
    p99  = [np.percentile(r, 99)  for r in reps]
    mean = [np.mean(r)            for r in reps]
    return dict(p50=np.array(p50), p95=np.array(p95),
                p99=np.array(p99), mean=np.array(mean))

# ── Carrega dados ─────────────────────────────────────────────────────────────
reps_rest = carregar_latencias("rest")
reps_msg  = carregar_latencias("msg")

todas_rest = np.concatenate(reps_rest)
todas_msg  = np.concatenate(reps_msg)

rest_limpo, n_out_rest = remover_outliers_iqr(todas_rest)
msg_limpo,  n_out_msg  = remover_outliers_iqr(todas_msg)

pct_rest = percentis_por_rep(reps_rest)
pct_msg  = percentis_por_rep(reps_msg)

# ── Testes estatísticos ───────────────────────────────────────────────────────
def testar(a, b, nome):
    _, p_sw_a = stats.shapiro(a[:50] if len(a) > 50 else a)
    _, p_sw_b = stats.shapiro(b[:50] if len(b) > 50 else b)
    normal = p_sw_a > ALPHA and p_sw_b > ALPHA
    if normal:
        stat, p = stats.ttest_rel(a, b) if len(a) == len(b) else stats.ttest_ind(a, b)
        teste = "t"
    else:
        stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        teste = "Mann-Whitney"
    print(f"[{nome}] Shapiro REST p={p_sw_a:.4f} | MSG p={p_sw_b:.4f} → {'normal' if normal else 'não-normal'}")
    print(f"[{nome}] {teste}: stat={stat:.4f}, p={p:.6f} → {'SIGNIFICATIVO' if p < ALPHA else 'não sig.'} (α={ALPHA})")
    return p, teste

print("\n=== Testes de hipótese — Cenário 1 ===")
p_p50,  t_p50  = testar(pct_rest["p50"],  pct_msg["p50"],  "P50")
p_p95,  t_p95  = testar(pct_rest["p95"],  pct_msg["p95"],  "P95")
p_mean, t_mean = testar(pct_rest["mean"], pct_msg["mean"], "Média")

# ── Gráfico 1: Violin com escala log ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))

partes_rest = ax.violinplot([rest_limpo], positions=[1], showmedians=True,
                             showextrema=True, widths=0.6)
partes_msg  = ax.violinplot([msg_limpo],  positions=[2], showmedians=True,
                             showextrema=True, widths=0.6)

for pc in partes_rest["bodies"]:
    pc.set_facecolor(COR_REST); pc.set_alpha(0.7)
for part in ["cmedians", "cmins", "cmaxes", "cbars"]:
    partes_rest[part].set_color(COR_REST)

for pc in partes_msg["bodies"]:
    pc.set_facecolor(COR_MSG); pc.set_alpha(0.7)
for part in ["cmedians", "cmins", "cmaxes", "cbars"]:
    partes_msg[part].set_color(COR_MSG)

# Anotação de outliers removidos
pct_out_rest = 100 * n_out_rest / len(todas_rest)
pct_out_msg  = 100 * n_out_msg  / len(todas_msg)
ax.text(1, rest_limpo.max() * 1.05, f"{n_out_rest} outliers\n({pct_out_rest:.1f}%)",
        ha="center", va="bottom", fontsize=8, color="gray")
ax.text(2, msg_limpo.max() * 1.05, f"{n_out_msg} outliers\n({pct_out_msg:.1f}%)",
        ha="center", va="bottom", fontsize=8, color="gray")

ax.set_yscale("log")
ax.set_ylabel("Latência fim-a-fim (ms) — escala log")
ax.set_xticks([1, 2])
ax.set_xticklabels(["REST", "Mensageria"])
ax.set_title("Cenário 1 — Latência sob carga constante (8 req/s, 2 min)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}"))
ax.grid(axis="y", linestyle="--", alpha=0.4)

patch_rest = mpatches.Patch(color=COR_REST, alpha=0.7, label="REST")
patch_msg  = mpatches.Patch(color=COR_MSG,  alpha=0.7, label="Mensageria")
ax.legend(handles=[patch_rest, patch_msg], loc="upper left")

plt.tight_layout()
saida1 = os.path.join(OUTPUT_DIR, "cenario1_violin_log.png")
plt.savefig(saida1, dpi=150)
plt.close()
print(f"\nSalvo: {saida1}")

# ── Gráfico 2: Percentis agrupados (P50 / P95 / P99) por versão ──────────────
labels  = ["P50", "P95", "P99"]
rest_vals = [np.mean(pct_rest["p50"]), np.mean(pct_rest["p95"]), np.mean(pct_rest["p99"])]
msg_vals  = [np.mean(pct_msg["p50"]),  np.mean(pct_msg["p95"]),  np.mean(pct_msg["p99"])]
rest_err  = [np.std(pct_rest["p50"]),  np.std(pct_rest["p95"]),  np.std(pct_rest["p99"])]
msg_err   = [np.std(pct_msg["p50"]),   np.std(pct_msg["p95"]),   np.std(pct_msg["p99"])]

x = np.arange(len(labels))
w = 0.35

fig, ax = plt.subplots(figsize=(8, 5))
b1 = ax.bar(x - w/2, rest_vals, w, yerr=rest_err, capsize=5,
            color=COR_REST, alpha=0.8, label="REST")
b2 = ax.bar(x + w/2, msg_vals,  w, yerr=msg_err,  capsize=5,
            color=COR_MSG,  alpha=0.8, label="Mensageria")

# Rótulos de valor em cima de cada barra
for bar in b1:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 20,
            f"{h:.0f}ms", ha="center", va="bottom", fontsize=8, color=COR_REST)
for bar in b2:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 20,
            f"{h:.0f}ms", ha="center", va="bottom", fontsize=8, color=COR_MSG)

ax.set_ylabel("Latência (ms)")
ax.set_title("Cenário 1 — Percentis de latência (média das repetições ± dp)")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.4)

# Significância no P95 (mais relevante)
sig_label = f"p={p_p95:.4f}*" if p_p95 < ALPHA else f"p={p_p95:.4f}"
y_max = max(msg_vals) + max(msg_err) + 200
ax.annotate("", xy=(x[1] + w/2, y_max - 100), xytext=(x[1] - w/2, y_max - 100),
            arrowprops=dict(arrowstyle="-", color="black"))
ax.text(x[1], y_max, sig_label, ha="center", fontsize=8)

plt.tight_layout()
saida2 = os.path.join(OUTPUT_DIR, "cenario1_percentis_agrupados.png")
plt.savefig(saida2, dpi=150)
plt.close()
print(f"Salvo: {saida2}")

# ── Gráfico 3: Evolução temporal da latência (MSG) — bimodalidade ─────────────
# Usa a rep 1 da MSG pra mostrar o comportamento ao longo do tempo
df_msg1 = pd.read_csv(os.path.join(RESULTS_DIR, "cenario1_msg_rep1.csv"))
metrica = "pedido_duration" if "pedido_duration" in df_msg1["metric_name"].values else "http_req_duration"
df_dur = df_msg1[df_msg1["metric_name"] == metrica][["timestamp", "metric_value"]].copy()
df_dur["timestamp"] = pd.to_numeric(df_dur["timestamp"])
df_dur = df_dur.sort_values("timestamp")
t0 = df_dur["timestamp"].iloc[0]
df_dur["t_rel"] = df_dur["timestamp"] - t0

fig, ax = plt.subplots(figsize=(9, 4))
ax.scatter(df_dur["t_rel"], df_dur["metric_value"],
           s=6, alpha=0.4, color=COR_MSG, label="Mensageria (rep 1)")
ax.axhline(5000, color="gray", linestyle="--", linewidth=0.8, label="Limite polling (5s)")
ax.set_xlabel("Tempo relativo (s)")
ax.set_ylabel("Latência fim-a-fim (ms)")
ax.set_title("Cenário 1 MSG — Distribuição temporal da latência (rep 1)")
ax.legend(fontsize=8)
ax.grid(linestyle="--", alpha=0.3)
plt.tight_layout()
saida3 = os.path.join(OUTPUT_DIR, "cenario1_msg_temporal.png")
plt.savefig(saida3, dpi=150)
plt.close()
print(f"Salvo: {saida3}")

print("\nPronto! Gráficos salvos em:", OUTPUT_DIR)
