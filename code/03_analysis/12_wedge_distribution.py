"""Fit one distribution of the wedge w to the per-project bounds from 10_wedge_bounds.py.

Run 10_wedge_bounds.py first.

10 gives each project a range for w (in MPDU discounts d), not a number, and 25 of
the ranges have no top (at 22% on the old schedule, w >= 0.325). To get a median and
a mean we assume w across projects follows a curve of a known shape, plus a mass p0
at zero for projects the density limit did not bind on, and pick the curve that
makes the observed ranges most likely (an interval-censored likelihood, as in a
Tobit). Each project contributes

  zero (below base)          w = 0               p0
  exact                      w                   (1 - p0) f(w)
  at base (upper bound)      0 < w <= hi         (1 - p0) F(hi)
  interval                   lo <= w <= hi       (1 - p0) (F(hi) - F(lo))
  at 22% (lower bound)       w >= lo             (1 - p0) (1 - F(lo))
  height limit               w >= 0              1: no information, assumed drawn
                                                 from the same curve
  own schedule, RMX, inside the last step: left out (no bound in 10)

f, F: density and CDF of the positive part, lognormal (gamma and Weibull as checks).
At base the limit binds, so w > 0 there and those ranges get no zero mass. p0 is
then the zeros over the zeros plus the other informative projects. Bounds that 10
states as averages over a step (the old last step, the CR lump) are used here as
bounds on w itself.

Checks:
  band   without any shape, the data bound the CDF of w: at each w, between the
         share of projects whose range ends at or below w and the share whose range
         starts at or below w (all bounded projects, height limit as [0, inf))
  counts on the old schedule the four positions cut w > 0 into four pieces (at base
         w <= 0.10, between 0.10-0.14, at 20% 0.14-0.325, at 22% above 0.325), so
         each fit predicts how many of the old-schedule bonus projects land in each
  boot   500 bootstrap draws over projects, lognormal
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parents[2]
BOUNDS = ROOT / "output" / "tables" / "wedge_bounds.csv"
FIT_FILE = ROOT / "output" / "tables" / "wedge_distribution.csv"
CHECK_FILE = ROOT / "output" / "tables" / "wedge_distribution_check.csv"
BOOT_FILE = ROOT / "output" / "tables" / "wedge_distribution_bootstrap.csv"
FIG_FILE = ROOT / "output" / "figures" / "wedge_distribution.pdf"

OLD_CUTS = [0.0, 0.10, 0.14, 0.325, np.inf]     # old schedule: at base, between, at 20%, at 22%
OLD_POSITION = {"upper": "at base", "exact": "between", "interval (average upper)": "at 20%",
                "lower (average)": "at 22%"}
N_BOOT = 500

# positive part of w: scipy distribution and its parameters from an unrestricted theta
FAMILIES = {
    "lognormal": (stats.lognorm, lambda t: dict(s=np.exp(t[1]), scale=np.exp(t[0]))),
    "gamma": (stats.gamma, lambda t: dict(a=np.exp(t[0]), scale=np.exp(t[1]))),
    "weibull": (stats.weibull_min, lambda t: dict(c=np.exp(t[0]), scale=np.exp(t[1]))),
}

BLUE, RED, GREEN, GRAY = "#5b7fa6", "#b04a4a", "#5a8a5a", "#888888"
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 10, "axes.spines.top": False, "axes.spines.right": False,
})


def ranges(d):
    """lo, hi and likelihood kind for each project with a bound."""
    d = d[d["w_lo"].notna()].copy()
    d["hi"] = d["w_hi"].fillna(np.inf)
    d["lo"] = d["w_lo"]
    d["kind"] = np.select([d["bound"] == "zero", d["bound"] == "height binds", d["lo"] == d["hi"]],
                          ["zero", "none", "exact"], "interval")
    return d


def fit(d, family):
    """p0 and the positive-part distribution that maximize the likelihood of the ranges."""
    dist, par = FAMILIES[family]
    ex = d.loc[d["kind"] == "exact", "lo"].to_numpy()
    lo = d.loc[d["kind"] == "interval", "lo"].to_numpy()
    hi = d.loc[d["kind"] == "interval", "hi"].to_numpy()
    n_zero, n_pos = (d["kind"] == "zero").sum(), len(ex) + len(lo)

    def nll(t):
        p = par(t)
        prob = dist.sf(lo, **p) - dist.sf(hi, **p)
        return -(dist.logpdf(ex, **p).sum() + np.log(np.maximum(prob, 1e-300)).sum())

    best = min((optimize.minimize(nll, t0, method="Nelder-Mead", options=dict(xatol=1e-8, fatol=1e-10, maxiter=5000))
                for t0 in ([np.log(0.3), 0.0], [0.0, np.log(0.3)], [np.log(0.1), 1.0], [1.0, np.log(0.1)])),
               key=lambda r: r.fun)
    p0 = n_zero / (n_zero + n_pos)
    loglik = -best.fun + n_zero * np.log(p0) + n_pos * np.log(1 - p0)
    return p0, dist(**par(best.x)), loglik


def summarize(p0, f):
    """Statistics of w = 0 with probability p0, else drawn from f."""
    q = lambda u: 0.0 if u <= p0 else f.ppf((u - p0) / (1 - p0))
    return dict(p0=p0, median=q(0.5), p75=q(0.75), p90=q(0.9), mean=(1 - p0) * f.mean(),
                median_if_binds=f.median(), mean_if_binds=f.mean(), share_above_0325=(1 - p0) * f.sf(0.325))


def main():
    d = ranges(pd.read_csv(BOUNDS))
    print(f"{len(d)} projects with a bound: " + ", ".join(f"{k} {v}" for k, v in d["kind"].value_counts().items()))

    # no shape: bounds on the median and mean
    print(f"\nNo shape assumed ({len(d)} projects): median between {d['lo'].median():.3f} and {d['hi'].median():.3f}; "
          f"mean at least {d['lo'].mean():.3f}, no upper bound")

    rows, fits = [], {}
    for family in FAMILIES:
        p0, f, loglik = fit(d, family)
        fits[family] = (p0, f)
        rows.append(dict(family=family, params=" ".join(f"{k}={v:.4g}" for k, v in f.kwds.items()),
                         loglik=loglik, **summarize(p0, f)))
    t = pd.DataFrame(rows)
    t.to_csv(FIT_FILE, index=False, float_format="%.4g")
    print("\nFits (w in d; median etc. over all informative projects, *_if_binds over w > 0):")
    print(t.round(3).to_string(index=False))

    # predicted vs observed positions, old-schedule bonus projects with w > 0
    old = d[(d["period"] == "old") & (d["group"] == "bonus available") & d["bound"].isin(OLD_POSITION)]
    obs = old["bound"].map(OLD_POSITION).value_counts().reindex(list(OLD_POSITION.values()))
    check = pd.DataFrame({"position": obs.index, "w_range": [f"{a:g}-{b:g}" for a, b in zip(OLD_CUTS[:-1], OLD_CUTS[1:])],
                          "observed": obs.to_numpy()})
    for family, (p0, f) in fits.items():
        check[family] = len(old) * np.diff(f.cdf(OLD_CUTS))
    check.to_csv(CHECK_FILE, index=False, float_format="%.3g")
    print(f"\nOld-schedule bonus projects with w > 0 ({len(old)}), observed vs predicted by position:")
    print(check.round(1).to_string(index=False))

    # bootstrap over projects, lognormal
    rng = np.random.default_rng(0)
    boot = []
    for _ in range(N_BOOT):
        s = d.iloc[rng.integers(0, len(d), len(d))]
        if (s["kind"] == "zero").all():
            continue
        boot.append(summarize(*fit(s, "lognormal")[:2]))
    boot = pd.DataFrame(boot)
    ci = pd.DataFrame({"estimate": pd.Series(summarize(*fits["lognormal"])),
                       "lo_2.5": boot.quantile(0.025), "hi_97.5": boot.quantile(0.975)})
    ci.to_csv(BOOT_FILE, float_format="%.4g")
    print(f"\nLognormal, {len(boot)} bootstrap draws over projects (95% percentile intervals):")
    print(ci.round(3).to_string())

    # figure: the band the data allow, and the fitted CDFs
    grid = np.linspace(0, 1.6, 801)
    lo_cdf = [(d["hi"] <= w).mean() for w in grid]
    hi_cdf = [(d["lo"] <= w).mean() for w in grid]
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.fill_between(grid, lo_cdf, hi_cdf, step="post", color=GRAY, alpha=0.3, lw=0,
                    label=f"allowed by the bounds alone ({len(d)} projects)")
    for (family, (p0, f)), color in zip(fits.items(), [BLUE, RED, GREEN]):
        ax.plot(grid, p0 + (1 - p0) * f.cdf(grid), color=color, lw=2, label=family)
    for v in OLD_CUTS[1:-1]:
        ax.axvline(v, color=GRAY, ls=":", lw=0.8)
    ax.text(0.325, 0.02, " old last step 0.325", fontsize=8, color="#444444")
    ax.set_xlim(0, 1.6)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Wedge w: value of one more permitted unit, in MPDU discounts d")
    ax.set_ylabel("Share of projects with wedge at most w")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG_FILE)
    fig.savefig(FIG_FILE.with_suffix(".png"), dpi=150)


if __name__ == "__main__":
    main()
