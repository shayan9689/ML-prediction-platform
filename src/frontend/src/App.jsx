import { Link, NavLink, Route, Routes } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Predict from "./pages/Predict.jsx";
import Performance from "./pages/Performance.jsx";

function Nav() {
  const link = ({ isActive }) =>
    `text-sm transition ${isActive ? "text-white" : "text-zinc-500 hover:text-zinc-200"}`;
  return (
    <header className="sticky top-0 z-20 border-b border-white/5 bg-black/40 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-3">
          <span className="h-8 w-8 rounded-xl bg-gradient-to-br from-zinc-100 via-zinc-500 to-zinc-800 shadow-glow" />
          <span className="font-display text-sm font-semibold tracking-tight text-white">ML Prediction</span>
        </Link>
        <nav className="flex gap-6">
          <NavLink to="/" className={link} end>
            Home
          </NavLink>
          <NavLink to="/performance?task=house_price" className={link} title="See how accurate each score is">
            Accuracy
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

export default function App() {
  return (
    <div className="page-bg min-h-screen">
      <Nav />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/predict/:taskId" element={<Predict />} />
          <Route path="/performance" element={<Performance />} />
        </Routes>
      </main>
      <footer className="mx-auto max-w-6xl px-6 pb-10 text-xs text-zinc-600">
        Tabular ML · scikit-learn / XGBoost · FastAPI. No LLM APIs. Built for portfolio walkthroughs.
      </footer>
    </div>
  );
}
