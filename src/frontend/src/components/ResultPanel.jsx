import { TASK_META } from "../formConfig.js";

function formatPrediction(taskId, result) {
  if (taskId === "house_price") {
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(
      result.prediction
    );
  }
  if (taskId === "churn") {
    const stay = result.prediction_label === "No";
    return stay ? "Likely to stay" : "Likely to churn";
  }
  return result.prediction_label === "high_risk" ? "Higher reject risk" : "Lower reject risk";
}

function subtitle(taskId, result) {
  if (taskId === "house_price") {
    return "Estimated median neighborhood value in USD. Training data is capped near $500,000.";
  }
  if (taskId === "churn") return `${(result.prediction * 100).toFixed(1)}% probability of leaving`;
  return `${(result.prediction * 100).toFixed(1)}% probability of reject / default`;
}

export default function ResultPanel({ taskId, result }) {
  const meta = TASK_META[taskId];
  const pct = Math.round((result.confidence || 0) * 100);
  return (
    <article className="gradient-border mt-6 animate-fadeUp rounded-3xl p-6 shadow-glow">
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-zinc-500">{meta?.resultTitle || "Result"}</p>
      <h3 className="font-display mt-2 text-3xl font-semibold tracking-tight text-white">{formatPrediction(taskId, result)}</h3>
      <p className="mt-2 text-sm text-zinc-400">{subtitle(taskId, result)}</p>
      <div className="mt-5">
        <div className="mb-1 flex justify-between text-xs text-zinc-500">
          <span>Confidence</span>
          <span className="text-zinc-300">{pct}%</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
          <div
            className="h-full origin-left rounded-full bg-gradient-to-r from-zinc-400 to-white transition-transform duration-700"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
      <div className="mt-5 flex flex-wrap gap-2 text-xs text-zinc-400">
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">Model · {result.model_used}</span>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
          {new Date(result.timestamp).toLocaleString()}
        </span>
      </div>
    </article>
  );
}
