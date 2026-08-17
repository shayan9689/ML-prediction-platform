import { useEffect, useId, useRef, useState } from "react";

export function normalizeOptions(options = []) {
  return options.map((opt) => (typeof opt === "object" ? opt : { value: opt, label: String(opt) }));
}

export default function ThemeSelect({ value, options, onChange, className = "" }) {
  const items = normalizeOptions(options);
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  const listId = useId();
  const selected = items.find((item) => String(item.value) === String(value)) || items[0];

  useEffect(() => {
    function onDoc(event) {
      if (!rootRef.current?.contains(event.target)) setOpen(false);
    }
    function onKey(event) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onKey);
    };
  }, []);

  return (
    <div ref={rootRef} className={`relative ${className}`}>
      <button
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listId}
        onClick={() => setOpen((prev) => !prev)}
        className="field-shell flex w-full items-center justify-between px-3.5 py-2.5 text-left text-sm text-zinc-100"
      >
        <span>{selected?.label || "Select"}</span>
        <svg
          className={`h-4 w-4 shrink-0 text-zinc-500 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
          viewBox="0 0 20 20"
          fill="none"
          aria-hidden="true"
        >
          <path d="M5 7.5 10 12.5 15 7.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {open ? (
        <ul
          id={listId}
          role="listbox"
          className="menu-panel absolute z-30 mt-2 max-h-64 w-full overflow-auto py-1"
        >
          {items.map((item) => {
            const active = String(item.value) === String(value);
            return (
              <li key={String(item.value)} role="option" aria-selected={active}>
                <button
                  type="button"
                  className={`flex w-full px-3.5 py-2 text-left text-sm transition ${
                    active ? "bg-white/10 text-white" : "text-zinc-300 hover:bg-white/5 hover:text-white"
                  }`}
                  onClick={() => {
                    onChange(item.value);
                    setOpen(false);
                  }}
                >
                  {item.label}
                </button>
              </li>
            );
          })}
        </ul>
      ) : null}
    </div>
  );
}
