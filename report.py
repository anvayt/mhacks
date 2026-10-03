"""Train the forecast model on real EIA-930 data and write a simple HTML report.

    python report.py                  # 120 days of MISO, last 14 days held out for testing
    python report.py --days 180 --test-days 21
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from plotly.offline import get_plotlyjs_version

import carbon_intensity as ci
import model as m

# Light-mode colors; the page swaps them for dark-mode equivalents when needed.
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE = "#2a78d6"
DARK = {SURFACE: "#1a1a19", INK: "#ffffff", INK2: "#c3c2b7", GRID: "#2c2c2a", AXIS: "#383835", BLUE: "#3987e5"}
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'
UNIT = "g CO₂ per kWh"


def _local(times) -> list[str]:
    return [t.strftime("%Y-%m-%d %H:%M") for t in pd.DatetimeIndex(times).tz_convert(m.LOCAL_TZ)]


def _layout(height, xtitle="", ytitle=UNIT, **kw):
    axis = lambda title: dict(title=dict(text=title, font=dict(color=INK2)), gridcolor=GRID, linecolor=AXIS,
                              showline=True, zeroline=False, tickfont=dict(color=MUTED))
    lay = dict(height=height, paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, font=dict(family=FONT, color=INK, size=13),
               margin=dict(l=70, r=30, t=40, b=60), xaxis=axis(xtitle), yaxis=axis(ytitle),
               legend=dict(orientation="h", y=1.12, x=0, font=dict(color=INK2)),
               hoverlabel=dict(bgcolor=SURFACE, bordercolor=AXIS, font=dict(color=INK, family=FONT)))
    lay.update(kw)
    return lay


def _bars(labels, values, colors, xtitle):
    data = [dict(type="bar", orientation="h", y=labels[::-1], x=[round(v, 1) for v in values[::-1]],
                 marker=dict(color=colors[::-1]), text=[f"{v:.0f}" for v in values[::-1]], textposition="outside",
                 textfont=dict(color=INK), cliponaxis=False, hovertemplate="%{y}: %{x:.1f}<extra></extra>")]
    lay = _layout(60 * len(labels) + 80, xtitle, "", showlegend=False, bargap=0.4, margin=dict(l=30, r=50, t=10, b=60))
    lay["yaxis"].update(automargin=True, showgrid=False)
    return dict(data=data, layout=lay)


def example_forecast(hist, preds):
    """One real 24h forecast from the test window, issued at 6 PM, vs. what happened."""
    P = pd.DataFrame(preds).dropna()
    evenings = P.index[P.index.tz_convert(m.LOCAL_TZ).hour == 18]
    t = evenings[len(evenings) // 2] if len(evenings) else P.index[len(P) // 2]
    hs = sorted(preds)
    times = [t + pd.Timedelta(hours=h) for h in hs]
    forecast = P.loc[t, hs].to_numpy()
    actual = hist[m.TARGET].reindex(times).to_numpy()
    pick = int(np.argmin(forecast))
    data = [
        dict(type="scatter", mode="lines", x=_local(times), y=actual.round(1).tolist(), name="What actually happened",
             line=dict(color=INK2, width=2), hovertemplate="Actual: %{y:.0f}<extra></extra>"),
        dict(type="scatter", mode="lines", x=_local(times), y=forecast.round(1).tolist(), name="Model's prediction",
             line=dict(color=BLUE, width=2), hovertemplate="Predicted: %{y:.0f}<extra></extra>"),
        dict(type="scatter", mode="markers+text", x=_local([times[pick]]), y=[float(forecast[pick])],
             name="Hour the model would pick", marker=dict(size=14, color=BLUE, symbol="star"),
             text=["model picks this hour"], textposition="bottom center", textfont=dict(color=INK2),
             hovertemplate="Picked hour<extra></extra>"),
    ]
    return dict(data=data, layout=_layout(380, "", UNIT, hovermode="x unified")), t.tz_convert(m.LOCAL_TZ)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ba", default="MISO")
    ap.add_argument("--days", type=int, default=120)
    ap.add_argument("--test-days", type=int, default=14)
    ap.add_argument("--out", default="reports/model_report.html")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    hist = ci.load_history(now - timedelta(days=args.days), now, args.ba)
    results, preds, test_start = m.train_and_test(hist, list(range(1, 25)), args.test_days)
    s = m.schedule_backtest(hist, preds)
    avg = lambda k: float(np.mean([r[k]["mae"] for r in results]))
    typical = float(hist[m.TARGET].mean())

    fig1, issued = example_forecast(hist, preds)
    fig2 = _bars(["Our model", "Copy the last known day", "Assume nothing changes"],
                 [avg("model"), avg("seasonal_naive"), avg("persistence")], [BLUE, MUTED, MUTED],
                 f"Average miss ({UNIT}), lower is better")
    fig3 = _bars(["Run it right away", "Run at the model's pick", "Run at the copy-last-day pick", "Best possible (hindsight)"],
                 [s["run_now"], s["model_pick"], s["yesterday_pick"], s["oracle"]], [MUTED, BLUE, MUTED, AXIS],
                 f"Carbon of the hour you ran it ({UNIT}), lower is better")
    figs = {"f1": fig1, "f2": fig2, "f3": fig3}

    body = f"""
<h1>Can we predict when MISO's grid is cleanest?</h1>
<p class="lead">Every hour, the model predicts how much CO₂ each kWh of MISO electricity will cost over the next 24 hours.
It learned from {args.days} days of real grid data. We then tested it on the last {args.test_days} days,
which it never saw ({test_start.tz_convert(m.LOCAL_TZ):%b %d} onward).</p>

<section><h2>1. What a prediction looks like</h2>
<p>A real prediction made {issued:%A %b %d at %-I %p}. Blue is what the model expected; gray is what actually happened.
The star is the hour it would tell you to run the dryer.</p>
<div id="f1"></div></section>

<section><h2>2. How far off is it?</h2>
<p>On average the prediction misses by about <b>{avg('model'):.0f} {UNIT}</b>. The grid usually sits around {typical:.0f},
so that's roughly a {100 * avg('model') / typical:.0f}% miss. For comparison, here are two shortcuts that use no model at all:</p>
<div id="f2"></div></section>

<section><h2>3. Does it actually help?</h2>
<p>We replayed the test period. Every hour, someone asks "when should I run my dryer in the next 24 hours?"
Following the model's pick uses electricity that's <b>{s['saving_vs_now_pct']:.0f}% cleaner</b> than running it right away.</p>
<div id="f3"></div></section>

<section><h2>Bottom line</h2>
<ul>
<li>Running at the model's pick saves about {s['saving_vs_now_pct']:.0f}% CO₂ compared with running right away.</li>
<li>Just copying the last known day gets almost the same result, so the model is only slightly better than that shortcut so far.</li>
<li>What's holding it back: the grid data it sees is about a day old, and it has no wind forecast, even though wind is
the biggest driver of MISO's clean hours.</li>
</ul></section>
"""
    css = """
:root{color-scheme:light;--bg:#f9f9f7;--card:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--line:rgba(11,11,11,.1)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#0d0d0d;--card:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--line:rgba(255,255,255,.1)}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#0d0d0d;--card:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--line:rgba(255,255,255,.1)}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:860px;margin:0 auto;padding:32px 16px 64px}
h1{font-size:28px;line-height:1.25;margin:0 0 8px}h2{font-size:20px;margin:0 0 6px}
.lead,section p{color:var(--ink2)}section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;margin:20px 0}
"""
    js = """
const dark = document.documentElement.dataset.theme === 'dark' ||
  (document.documentElement.dataset.theme !== 'light' && matchMedia('(prefers-color-scheme: dark)').matches);
for (const [id, fig] of Object.entries(FIGS)) {
  let s = JSON.stringify(fig);
  if (dark) s = s.replace(/#[0-9a-f]{6}/gi, h => DARK[h.toLowerCase()] || h);
  const f = JSON.parse(s);
  Plotly.newPlot(id, f.data, f.layout, {displayModeBar: false, responsive: true});
}
"""
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Clean Hours Forecast</title><style>{css}</style>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@{get_plotlyjs_version()}/plotly.min.js"></script></head>
<body><main>{body}</main><script>const FIGS = {json.dumps(figs)}; const DARK = {json.dumps(DARK)};{js}</script></body></html>"""
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
