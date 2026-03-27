"""
================================================================================
STRAVA x RUNNA M&A ANALYSIS
W3 — The Deal & Strategy Project
Author: Zama López Linhardt
================================================================================

RESEARCH SOURCES (full reference list):
[1] Strava revenue & user data: Bloomberg / company disclosures, 2022–2025
[2] Strava IPO filing / Goldman Sachs: Reuters, January 2026
[3] Runna ARR estimate: Sensor Tower, March 2025
[4] Runna subscriber & pricing data: Runna press release, April 2025
[5] Deal announcement & strategic rationale: Strava blog, April 17 2025
[6] Combined subscription launch: Strava blog, July 2 2025
[7] Fatmap acquisition & shutdown: DC Rainmaker, 2024
[8] DC Rainmaker acquisition commentary: dcrainmaker.com, April 2025
[9] Under Armour connected fitness case: Harvard Business Review / UA earnings, 2019
[10] SaaS M&A revenue multiples: Dealroom / PitchBook, 2024–2025
[11] Runna deal valuation estimate: Dealroom, 2025
[12] User reaction / community backlash: Strava community hub / Reddit r/running, 2025
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ── Global style ──────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font="DejaVu Sans")
PALETTE = {
    "bull":    "#2ecc71",
    "base":    "#3498db",
    "bear":    "#e74c3c",
    "neutral": "#95a5a6",
    "dark":    "#2c3e50",
    "accent":  "#f39c12",
}
plt.rcParams.update({
    "figure.facecolor":  "white",
    "axes.facecolor":    "white",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.labelsize":    11,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "legend.fontsize":   9,
    "figure.dpi":        150,
})

# ══════════════════════════════════════════════════════════════════════════════
# 1. ASSUMPTIONS BLOCK  (edit here to stress-test any scenario)
# ══════════════════════════════════════════════════════════════════════════════

# ── Strava base metrics [1][2] ─────────────────────────────────────────────
STRAVA_REGISTERED_USERS   = 150_000_000   # registered users
STRAVA_PAYING_USERS       = 7_500_000     # ~5% monetised [2]
STRAVA_FREE_USERS         = STRAVA_REGISTERED_USERS - STRAVA_PAYING_USERS
STRAVA_REVENUE_2024       = 338_000_000   # USD [1]
STRAVA_PREMIUM_PRICE      = 79.99         # USD/year
STRAVA_BLENDED_ARPU       = STRAVA_REVENUE_2024 / STRAVA_PAYING_USERS

# ── Runna base metrics [3][4] ──────────────────────────────────────────────
RUNNA_ARR_PRE_DEAL        = 40_000_000    # USD ARR, Sensor Tower estimate [3]
RUNNA_SUBSCRIBERS         = 90_000        # paying subscribers pre-deal [4]
RUNNA_PRICE_STANDALONE    = 119.99        # USD/year [4]
RUNNA_GROWTH_RATE         = 0.30          # conservative (was 30x in 2022–23) [4]

# ── Deal assumptions [5][10][11] ───────────────────────────────────────────
DEAL_PRICE_LOW            = 40_000_000    # Dealroom floor estimate [11]
DEAL_PRICE_MID            = 120_000_000   # 3x ARR — SaaS median [10]
DEAL_PRICE_HIGH           = 200_000_000   # 5x ARR — premium (profitable, high retention) [10]

# ── Combined bundle [6] ────────────────────────────────────────────────────
BUNDLE_PRICE              = 149.99        # USD/year [6]

# ── ARPU uplift conversion rates (% of Strava FREE users buying bundle) ────
CONV_CONSERVATIVE         = 0.02          # 2%
CONV_BASE                 = 0.05          # 5%
CONV_OPTIMISTIC           = 0.10          # 10%

# ── Integration scenario parameters (36-month horizon) ────────────────────
MONTHS                    = np.arange(0, 37)

# ══════════════════════════════════════════════════════════════════════════════
# 2. DEAL VALUATION SANITY CHECK
# ══════════════════════════════════════════════════════════════════════════════

def deal_valuation_analysis():
    multiples     = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    implied_vals  = [RUNNA_ARR_PRE_DEAL * m / 1e6 for m in multiples]   # $M
    saas_median   = 3.8   # PitchBook 2025 median [10]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Deal Valuation Sanity Check — Strava × Runna", fontsize=14,
                 fontweight="bold", color=PALETTE["dark"], y=1.01)

    # ── Left: implied valuation bar chart ─────────────────────────────────
    ax = axes[0]
    colors = [PALETTE["bear"] if m < saas_median
              else PALETTE["bull"] if m <= 5
              else PALETTE["accent"] for m in multiples]
    bars = ax.bar([f"{m}x" for m in multiples], implied_vals, color=colors,
                  width=0.55, edgecolor="white", linewidth=0.8)
    ax.axhline(DEAL_PRICE_LOW  / 1e6, color=PALETTE["bear"],    ls="--", lw=1.3,
               label=f"Dealroom floor  ${DEAL_PRICE_LOW/1e6:.0f}M")
    ax.axhline(DEAL_PRICE_MID  / 1e6, color=PALETTE["base"],    ls="--", lw=1.3,
               label=f"3x ARR estimate  ${DEAL_PRICE_MID/1e6:.0f}M")
    ax.axhline(DEAL_PRICE_HIGH / 1e6, color=PALETTE["bull"],    ls="--", lw=1.3,
               label=f"5x ARR premium   ${DEAL_PRICE_HIGH/1e6:.0f}M")
    for bar, val in zip(bars, implied_vals):
        ax.text(bar.get_x() + bar.get_width()/2, val + 2, f"${val:.0f}M",
                ha="center", va="bottom", fontsize=8.5, color=PALETTE["dark"])
    ax.set_title("Implied Valuation at Different Revenue Multiples")
    ax.set_xlabel("Revenue Multiple (x ARR)")
    ax.set_ylabel("Implied Valuation (USD millions)")
    ax.legend(loc="upper left", framealpha=0.9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))

    # ── Right: multiple context vs SaaS comps ─────────────────────────────
    ax2 = axes[1]
    comp_labels = ["SaaS Median\n2024", "SaaS Median\n2025",
                   "Runna Low\nEstimate", "Runna Mid\nEstimate",
                   "Runna High\nEstimate"]
    comp_vals   = [2.9, 3.8,
                   DEAL_PRICE_LOW  / RUNNA_ARR_PRE_DEAL,
                   DEAL_PRICE_MID  / RUNNA_ARR_PRE_DEAL,
                   DEAL_PRICE_HIGH / RUNNA_ARR_PRE_DEAL]
    comp_colors = [PALETTE["neutral"], PALETTE["neutral"],
                   PALETTE["bear"], PALETTE["base"], PALETTE["bull"]]
    bars2 = ax2.bar(comp_labels, comp_vals, color=comp_colors,
                    width=0.55, edgecolor="white", linewidth=0.8)
    ax2.axhline(saas_median, color=PALETTE["accent"], ls="--", lw=1.5,
                label=f"2025 SaaS median ({saas_median}x)")
    for bar, val in zip(bars2, comp_vals):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.05, f"{val:.1f}x",
                 ha="center", va="bottom", fontsize=8.5, color=PALETTE["dark"])
    ax2.set_title("Runna Multiple vs. SaaS Market Comparables")
    ax2.set_ylabel("Revenue Multiple (x ARR)")
    ax2.legend(framealpha=0.9)

    plt.tight_layout()
    plt.savefig("/home/claude/fig1_deal_valuation.png", bbox_inches="tight")
    plt.close()
    print("✓ Fig 1 saved: Deal Valuation Sanity Check")

    # Print summary
    print("\n── DEAL VALUATION SUMMARY ──────────────────────────────────────")
    print(f"   Runna ARR (pre-deal):       ${RUNNA_ARR_PRE_DEAL/1e6:.0f}M")
    print(f"   Dealroom floor estimate:    ${DEAL_PRICE_LOW/1e6:.0f}M  ({DEAL_PRICE_LOW/RUNNA_ARR_PRE_DEAL:.1f}x ARR)")
    print(f"   Mid estimate (3x ARR):      ${DEAL_PRICE_MID/1e6:.0f}M  ({DEAL_PRICE_MID/RUNNA_ARR_PRE_DEAL:.1f}x ARR)")
    print(f"   Premium estimate (5x ARR):  ${DEAL_PRICE_HIGH/1e6:.0f}M  ({DEAL_PRICE_HIGH/RUNNA_ARR_PRE_DEAL:.1f}x ARR)")
    print(f"   2025 SaaS median multiple:  {saas_median}x")
    print(f"   Verdict: At 3x, deal is at-market. At 5x, premium justified\n"
          f"            only if Runna sustains >25% ARR growth post-acquisition.")

# ══════════════════════════════════════════════════════════════════════════════
# 3. ARPU UPLIFT MODEL
# ══════════════════════════════════════════════════════════════════════════════

def arpu_uplift_model():
    scenarios = {
        "Conservative (2%)": CONV_CONSERVATIVE,
        "Base Case (5%)":    CONV_BASE,
        "Optimistic (10%)":  CONV_OPTIMISTIC,
    }
    colors = [PALETTE["bear"], PALETTE["base"], PALETTE["bull"]]

    results = {}
    for label, conv in scenarios.items():
        new_bundle_subs   = STRAVA_FREE_USERS * conv
        bundle_revenue    = new_bundle_subs * BUNDLE_PRICE
        total_revenue     = STRAVA_REVENUE_2024 + bundle_revenue
        total_paying      = STRAVA_PAYING_USERS + new_bundle_subs
        new_blended_arpu  = total_revenue / total_paying
        arpu_uplift_pct   = (new_blended_arpu - STRAVA_BLENDED_ARPU) / STRAVA_BLENDED_ARPU * 100
        revenue_uplift    = bundle_revenue
        results[label] = {
            "new_subs":        new_bundle_subs,
            "bundle_rev":      bundle_revenue,
            "total_rev":       total_revenue,
            "new_arpu":        new_blended_arpu,
            "arpu_uplift_pct": arpu_uplift_pct,
        }

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("ARPU Uplift Model — Bundle Conversion Impact on Strava Revenue",
                 fontsize=14, fontweight="bold", color=PALETTE["dark"], y=1.01)

    labels  = list(results.keys())
    metrics = ["new_subs", "bundle_rev", "new_arpu"]
    titles  = ["New Bundle Subscribers", "Incremental Bundle Revenue (USD)",
               "Blended ARPU Before vs. After"]

    for i, (ax, metric, title) in enumerate(zip(axes, metrics, titles)):
        if metric == "new_arpu":
            # Before/after comparison
            befores = [STRAVA_BLENDED_ARPU] * 3
            afters  = [results[l]["new_arpu"] for l in labels]
            x       = np.arange(len(labels))
            w       = 0.35
            b1 = ax.bar(x - w/2, befores, w, label="Before",
                        color=PALETTE["neutral"], edgecolor="white")
            b2 = ax.bar(x + w/2, afters,  w, label="After",
                        color=colors,           edgecolor="white")
            ax.set_xticks(x)
            ax.set_xticklabels([l.split(" ")[0] for l in labels])
            for bar in list(b1) + list(b2):
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 0.3,
                        f"${bar.get_height():.1f}",
                        ha="center", va="bottom", fontsize=7.5)
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}"))
            ax.legend()
        else:
            vals = [results[l][metric] for l in labels]
            bars = ax.bar(labels, vals, color=colors, edgecolor="white", width=0.5)
            fmt  = (lambda v: f"{v/1e6:.1f}M") if metric == "new_subs" \
                   else (lambda v: f"${v/1e6:.0f}M")
            for bar, val in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() * 1.01,
                        fmt(val), ha="center", va="bottom", fontsize=8)
            if metric == "bundle_rev":
                ax.yaxis.set_major_formatter(
                    mticker.FuncFormatter(lambda x, _: f"${x/1e6:.0f}M"))
            else:
                ax.yaxis.set_major_formatter(
                    mticker.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M"))
        ax.set_title(title)
        ax.set_xlabel("Scenario")
        ax.tick_params(axis="x", rotation=10)

    plt.tight_layout()
    plt.savefig("/home/claude/fig2_arpu_uplift.png", bbox_inches="tight")
    plt.close()
    print("✓ Fig 2 saved: ARPU Uplift Model")

    print("\n── ARPU UPLIFT SUMMARY ─────────────────────────────────────────")
    print(f"   Strava blended ARPU (baseline):  ${STRAVA_BLENDED_ARPU:.2f}/year")
    for label, r in results.items():
        print(f"\n   {label}")
        print(f"     New bundle subs:     {r['new_subs']/1e6:.1f}M")
        print(f"     Incremental revenue: ${r['bundle_rev']/1e6:.0f}M")
        print(f"     New blended ARPU:    ${r['new_arpu']:.2f} ({r['arpu_uplift_pct']:+.1f}%)")

# ══════════════════════════════════════════════════════════════════════════════
# 4. INTEGRATION RISK SCENARIO MODEL (36-month horizon)
# ══════════════════════════════════════════════════════════════════════════════

def integration_risk_model():
    """
    Three paths modelled over 36 months:
      Bull  — Successful integration: brand preserved, coaching deepens,
               subscriber growth accelerates via Strava distribution
      Base  — Stagnation (Fatmap precedent [7]): product slows, team attrition,
               Runna flatlines then declines
      Bear  — Brand damage (UA/MyFitnessPal precedent [9]): integration rushed,
               Runna identity absorbed, subscriber churn accelerates
    """
    t = MONTHS  # 0..36

    # Monthly subscriber trajectories (starting from 90,000)
    s0 = RUNNA_SUBSCRIBERS

    bull = s0 * (1 + 0.025) ** t          # +2.5%/month — distribution flywheel
    base = s0 * (1 + 0.005) ** t          # +0.5%/month — modest growth, slowing
    bear = s0 * np.where(
        t <= 12,
        (1 + 0.002) ** t,                 # slow growth initially
        (1 + 0.002) ** 12 * (0.975) ** (t - 12)  # then -2.5%/month churn
    )

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Integration Risk Scenarios — Runna Subscriber Trajectory (36 Months)",
                 fontsize=14, fontweight="bold", color=PALETTE["dark"], y=1.01)

    # ── Left: subscriber trajectories ─────────────────────────────────────
    ax = axes[0]
    ax.plot(t, bull / 1e3, color=PALETTE["bull"],    lw=2.2, label="Bull — Successful Integration")
    ax.plot(t, base / 1e3, color=PALETTE["base"],    lw=2.2, label="Base — Stagnation (Fatmap precedent)")
    ax.plot(t, bear / 1e3, color=PALETTE["bear"],    lw=2.2, label="Bear — Brand Damage (UA precedent)",
            ls="--")
    ax.axvline(12, color=PALETTE["neutral"], ls=":", lw=1.2, label="Month 12 — IPO window")
    ax.axvline(24, color=PALETTE["accent"],  ls=":", lw=1.2, label="Month 24 — Integration decision point")
    ax.fill_between(t, bear/1e3, bull/1e3, alpha=0.07, color=PALETTE["base"])
    ax.set_xlabel("Months Post-Acquisition")
    ax.set_ylabel("Runna Paying Subscribers (thousands)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}K"))
    ax.legend(fontsize=8, loc="upper left")
    ax.set_title("Subscriber Trajectory by Scenario")

    # ── Right: implied ARR at month 12, 24, 36 ────────────────────────────
    ax2      = axes[1]
    checkpoints = [12, 24, 36]
    bull_arr = [bull[m] * RUNNA_PRICE_STANDALONE / 1e6 for m in checkpoints]
    base_arr = [base[m] * RUNNA_PRICE_STANDALONE / 1e6 for m in checkpoints]
    bear_arr = [bear[m] * RUNNA_PRICE_STANDALONE / 1e6 for m in checkpoints]
    x        = np.arange(len(checkpoints))
    w        = 0.25
    ax2.bar(x - w,   bull_arr, w, color=PALETTE["bull"],    label="Bull",  edgecolor="white")
    ax2.bar(x,       base_arr, w, color=PALETTE["base"],    label="Base",  edgecolor="white")
    ax2.bar(x + w,   bear_arr, w, color=PALETTE["bear"],    label="Bear",  edgecolor="white",
            alpha=0.85)
    ax2.axhline(RUNNA_ARR_PRE_DEAL / 1e6, color=PALETTE["neutral"], ls="--",
                lw=1.3, label=f"Pre-deal ARR (${RUNNA_ARR_PRE_DEAL/1e6:.0f}M)")
    for bars_grp, arr_list in zip([x-w, x, x+w],
                                  [bull_arr, base_arr, bear_arr]):
        for xi, val in zip(bars_grp, arr_list):
            ax2.text(xi, val + 0.3, f"${val:.0f}M",
                     ha="center", va="bottom", fontsize=7.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(["Month 12\n(IPO window)", "Month 24\n(Integration decision)",
                          "Month 36\n(3-year horizon)"])
    ax2.set_ylabel("Implied Runna ARR (USD millions)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
    ax2.legend(fontsize=8)
    ax2.set_title("Implied Runna ARR at Key Checkpoints")

    plt.tight_layout()
    plt.savefig("/home/claude/fig3_integration_risk.png", bbox_inches="tight")
    plt.close()
    print("✓ Fig 3 saved: Integration Risk Scenarios")

    print("\n── INTEGRATION RISK SUMMARY ────────────────────────────────────")
    for m in [12, 24, 36]:
        print(f"\n   Month {m}:")
        print(f"     Bull: {bull[m]/1e3:.0f}K subs  "
              f"(${bull[m]*RUNNA_PRICE_STANDALONE/1e6:.0f}M ARR)")
        print(f"     Base: {base[m]/1e3:.0f}K subs  "
              f"(${base[m]*RUNNA_PRICE_STANDALONE/1e6:.0f}M ARR)")
        print(f"     Bear: {bear[m]/1e3:.0f}K subs  "
              f"(${bear[m]*RUNNA_PRICE_STANDALONE/1e6:.0f}M ARR)")

# ══════════════════════════════════════════════════════════════════════════════
# 5. DEAL SENSITIVITY HEATMAP
#    How does deal ROI change across (acquisition price) x (Runna ARR growth)?
# ══════════════════════════════════════════════════════════════════════════════

def sensitivity_heatmap():
    growth_rates  = np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40])
    deal_prices   = np.array([40, 80, 120, 160, 200])          # $M
    exit_multiple = 4.0   # conservative exit at 4x ARR in year 3
    years         = 3

    # ROI = (exit value - deal price) / deal price
    roi_matrix = np.zeros((len(deal_prices), len(growth_rates)))
    for i, price in enumerate(deal_prices):
        for j, g in enumerate(growth_rates):
            arr_y3     = RUNNA_ARR_PRE_DEAL * (1 + g) ** years / 1e6
            exit_val   = arr_y3 * exit_multiple
            roi        = (exit_val - price) / price * 100
            roi_matrix[i, j] = roi

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.heatmap(
        roi_matrix,
        annot=True,
        fmt=".0f",
        cmap="RdYlGn",
        center=0,
        xticklabels=[f"{int(g*100)}%" for g in growth_rates],
        yticklabels=[f"${p}M" for p in deal_prices],
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "3-Year ROI (%)"},
        ax=ax,
    )
    ax.set_title("Deal ROI Sensitivity — Acquisition Price × Runna ARR Growth Rate\n"
                 f"(Assumes 4x ARR exit multiple at year 3)",
                 fontsize=13, fontweight="bold", color=PALETTE["dark"])
    ax.set_xlabel("Runna Annual ARR Growth Rate (post-acquisition)")
    ax.set_ylabel("Acquisition Price (USD millions)")
    plt.tight_layout()
    plt.savefig("/home/claude/fig4_sensitivity_heatmap.png", bbox_inches="tight")
    plt.close()
    print("✓ Fig 4 saved: Deal ROI Sensitivity Heatmap")
    print("\n   Key read: green = deal looks cheap at that price/growth combo,")
    print("             red   = Strava overpaid relative to growth delivered.")

# ══════════════════════════════════════════════════════════════════════════════
# RUN ALL
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 65)
    print("  STRAVA × RUNNA M&A ANALYSIS — W3 Deal & Strategy Project")
    print("=" * 65)

    print("\n[1/4] Running deal valuation analysis...")
    deal_valuation_analysis()

    print("\n[2/4] Running ARPU uplift model...")
    arpu_uplift_model()

    print("\n[3/4] Running integration risk scenarios...")
    integration_risk_model()

    print("\n[4/4] Running deal sensitivity heatmap...")
    sensitivity_heatmap()

    print("\n" + "=" * 65)
    print("  All outputs saved to /home/claude/")
    print("  Figures: fig1_deal_valuation.png")
    print("           fig2_arpu_uplift.png")
    print("           fig3_integration_risk.png")
    print("           fig4_sensitivity_heatmap.png")
    print("=" * 65)
