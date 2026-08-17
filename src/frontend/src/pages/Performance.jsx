import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api.js";
import ThemeSelect from "../components/ThemeSelect.jsx";
import { TASK_META } from "../formConfig.js";

const TASKS = Object.values(TASK_META);

function metricCards(task, metrics) {
  if (!metrics) return [];
  if (task === "house_price") {
    return [
      ["Typical miss", metrics.rmse, "RMSE · how far off a guess usually is (big misses count more). Lower is better."],
      ["Average miss", metrics.mae, "MAE · plain average of |predicted − real| in dollars. Lower is better."],
      ["Fit quality", metrics.r2, "R² · 1.00 = perfect, 0 = no better than guessing the average price. Higher is better."],
    ];
  }
  return [
    ["Correct calls", metrics.accuracy, "Share of Yes/No labels the model got right. Easy to inflate if most people stay."],
    ["Balance score", metrics.f1, "F1 · mixes “when it says yes, is it right?” and “did it catch the real yeses?”"],
    ["Ranking quality", metrics.roc_auc, "ROC-AUC · 0.50 = coin flip, 1.00 = perfect at ranking risky vs safe."],
  ];
}

function fmt(task, label, value) {
  if (value == null) return "—";
  if (task === "house_price" && (label === "Typical miss" || label === "Average miss")) {
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
  }
  if (label === "Fit quality") return `${(value * 100).toFixed(0)} / 100`;
  if (["Correct calls", "Balance score", "Ranking quality"].includes(label)) {
    return `${(value * 100).toFixed(1)}%`;
  }
  if (Math.abs(value) >= 1000) return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
  return Number(value).toFixed(3);
}

const tooltipStyle = {
  background: "#121214",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: 12,
  color: "#e4e4e7",
};

export default function Performance() {
  const [params, setParams] = useSearchParams();
  const task = params.get("task") || "house_price";
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setError("");
    setData(null);
    api
      .metrics(task)
      .then(setData)
      .catch((err) => setError(err.message));
  }, [task]);

  const cards = metricCards(task, data?.metrics);
  const comparison = useMemo(() => {
    const rows = data?.comparison || [];
    const key = task === "house_price" ? "r2" : "roc_auc";
    return rows.map((row) => ({
      name: String(row.model || "model").replaceAll("_", " "),
      score: row[key] ?? 0,
    }));
  }, [data, task]);

  return (
    <section className="animate-fadeUp">
      <Link to="/" className="text-xs font-medium uppercase tracking-[0.16em] text-zinc-500 hover:text-zinc-300">
        ← Home
      </Link>
      <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-semibold text-white">Accuracy</h1>
          <p className="mt-2 max-w-xl text-sm leading-relaxed text-zinc-400">
            This is <span className="text-zinc-200">not</span> a copy of the form you just scored.
            Predict = one answer for the values you typed. Accuracy = overall quality of the model from training
            (test-set report). It stays the same until we retrain.
          </p>
          <p className="mt-2 text-sm text-zinc-500">
            Saved winner: <span className="text-zinc-300">{data?.best_model || "—"}</span>
            {" · "}
            <Link to={`/predict/${task}`} className="text-zinc-300 underline-offset-2 hover:text-white hover:underline">
              Back to Predict
            </Link>
          </p>
        </div>
        <div className="min-w-56 text-xs uppercase tracking-[0.14em] text-zinc-500">
          <span className="mb-1.5 block">Task</span>
          <ThemeSelect
            value={task}
            options={TASKS.map((t) => ({ value: t.id, label: t.name }))}
            onChange={(next) => setParams({ task: next })}
          />
        </div>
      </div>

      {error ? (
        <p className="mt-6 rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p>
      ) : null}

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {cards.map(([label, value, hint]) => (
          <article key={label} className="gradient-border rounded-3xl p-5">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-zinc-500">{label}</p>
            <p className="mt-2 font-display text-3xl text-white">{fmt(task, label, value)}</p>
            <p className="mt-1 text-xs text-zinc-500">{hint}</p>
          </article>
        ))}
      </div>

      <div className="mt-6 grid gap-5 lg:grid-cols-2">
        <article className="gradient-border rounded-3xl p-5">
          <h2 className="text-sm font-semibold text-zinc-200">Which algorithm won</h2>
          <div className="mt-3 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparison}>
                <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#a1a1aa" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#a1a1aa" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="score" fill="#d4d4d8" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
        <article className="gradient-border rounded-3xl p-5">
          <h2 className="text-sm font-semibold text-zinc-200">What the model listens to</h2>
          <div className="mt-3 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[...(data?.feature_importance || [])].slice(0, 8).reverse()} layout="vertical" margin={{ left: 8 }}>
                <CartesianGrid stroke="rgba(255,255,255,0.06)" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11, fill: "#a1a1aa" }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="feature" width={120} tick={{ fontSize: 10, fill: "#a1a1aa" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="importance" fill="#a1a1aa" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
      </div>
      <p className="mt-6 text-sm text-zinc-500">
        Housing values are capped at $500,001 in training. Churn and loan labels are imbalanced — AUC/F1 matter more than accuracy.
      </p>
    </section>
  );
}
