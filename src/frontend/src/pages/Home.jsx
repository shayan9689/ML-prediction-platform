import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import { TASK_META } from "../formConfig.js";

const ORDER = ["house_price", "churn", "loan_default"];

export default function Home() {
  const [live, setLive] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .health()
      .then(() => setLive(true))
      .catch((err) => {
        setLive(false);
        setError(err.message);
      });
  }, []);

  return (
    <section>
      <div className="max-w-3xl animate-fadeUp">
        <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-zinc-500">Decisioning studio</p>
        <h1 className="font-display mt-3 text-4xl font-semibold tracking-tight text-white md:text-5xl">
          Three client-ready scores.
          <span className="block bg-gradient-to-r from-zinc-100 via-zinc-400 to-zinc-600 bg-clip-text text-transparent">
            No coordinates. No raw columns.
          </span>
        </h1>
        <p className="mt-4 max-w-2xl text-sm leading-relaxed text-zinc-400 md:text-base">
          Pick a score, fill a short form, get a result. Accuracy shows how reliable that score is on test data.
        </p>
      </div>

      {!live ? (
        <p className="mt-6 rounded-2xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
          API is offline. Start FastAPI on port 8000 to score. Forms still load for review. {error}
        </p>
      ) : null}

      <div className="stagger mt-10 grid gap-5 md:grid-cols-3">
        {ORDER.map((id) => {
          const task = TASK_META[id];
          return (
            <article key={id} className="gradient-border group rounded-3xl p-6 transition duration-300 hover:-translate-y-1 hover:shadow-glow">
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-zinc-500">{task.kicker}</p>
              <h2 className="font-display mt-2 text-xl font-semibold text-white">{task.name}</h2>
              <p className="mt-3 min-h-[4.5rem] text-sm leading-relaxed text-zinc-400">{task.description}</p>
              <div className="mt-6 flex gap-3">
                <Link
                  to={`/predict/${id}`}
                  className="rounded-xl bg-gradient-to-r from-zinc-100 to-zinc-400 px-4 py-2 text-sm font-semibold text-zinc-950 transition hover:from-white hover:to-zinc-300"
                >
                  Predict
                </Link>
                <Link
                  to={`/performance?task=${id}`}
                  className="rounded-xl border border-white/10 px-4 py-2 text-sm font-medium text-zinc-300 hover:border-white/25"
                >
                  Accuracy
                </Link>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
