import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";
import Field from "../components/Field.jsx";
import ResultPanel from "../components/ResultPanel.jsx";
import { defaultForm, SCENARIOS, TASK_META, toModelPayload, visibleGroups } from "../formConfig.js";

export default function Predict() {
  const { taskId } = useParams();
  const meta = TASK_META[taskId] || { name: "Predict" };
  const [form, setForm] = useState(() => defaultForm(taskId));
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setForm(defaultForm(taskId));
    setResult(null);
    setError("");
  }, [taskId]);

  const groups = useMemo(() => visibleGroups(taskId, form), [taskId, form]);
  const scenarios = SCENARIOS[taskId] || [];

  function applyScenario(id) {
    const hit = scenarios.find((s) => s.id === id);
    if (!hit) return;
    setForm(hit.values);
    setResult(null);
    setError("");
  }

  async function onSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const payload = toModelPayload(taskId, form);
      const data = await api.predict(taskId, payload);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="animate-fadeUp">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <Link to="/" className="text-xs font-medium uppercase tracking-[0.16em] text-zinc-500 hover:text-zinc-300">
            ← Home
          </Link>
          <h1 className="font-display mt-3 text-3xl font-semibold text-white">{meta.name}</h1>
          <p className="mt-2 max-w-xl text-sm text-zinc-400">{meta.description}</p>
        </div>
        <Link to={`/performance?task=${taskId}`} className="text-sm text-zinc-400 hover:text-white">
          Accuracy →
        </Link>
      </div>

      {scenarios.length ? (
        <div className="mb-5 flex flex-wrap gap-2">
          <span className="self-center text-xs uppercase tracking-[0.16em] text-zinc-600">Try a profile</span>
          {scenarios.map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => applyScenario(s.id)}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-zinc-300 transition hover:border-white/30 hover:bg-white/10"
            >
              {s.label}
            </button>
          ))}
        </div>
      ) : null}

      <form onSubmit={onSubmit} className="gradient-border space-y-8 rounded-3xl p-6 md:p-8">
        {groups.map((group) => (
          <fieldset key={group.title}>
            <legend className="font-display text-sm font-semibold uppercase tracking-[0.14em] text-zinc-300">
              {group.title}
            </legend>
            {group.note ? <p className="mt-2 text-xs text-zinc-500">{group.note}</p> : null}
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              {group.fields.map((field) => (
                <Field
                  key={field.name}
                  field={field}
                  value={form[field.name]}
                  onChange={(next) => setForm((prev) => ({ ...prev, [field.name]: next }))}
                />
              ))}
            </div>
          </fieldset>
        ))}
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={loading}
            className="rounded-xl bg-gradient-to-r from-zinc-100 to-zinc-400 px-5 py-2.5 text-sm font-semibold text-zinc-950 transition hover:from-white hover:to-zinc-200 disabled:opacity-50"
          >
            {loading ? "Scoring…" : "Run prediction"}
          </button>
          <p className="text-xs text-zinc-500">Classical ML only — no OpenAI key required.</p>
        </div>
      </form>

      {error ? (
        <p className="mt-5 rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p>
      ) : null}

      {result ? <ResultPanel taskId={taskId} result={result} /> : null}
    </section>
  );
}
