import ThemeSelect, { normalizeOptions } from "./ThemeSelect.jsx";

export default function Field({ field, value, onChange }) {
  const options = normalizeOptions(field.options);
  const isSelect = field.type === "select";
  const prefix = field.prefix || (field.type === "currency" ? "$" : null);
  const unit = field.suffix;

  return (
    <div className="block text-sm">
      <span className="mb-1.5 block font-medium text-zinc-200">{field.label}</span>
      {isSelect ? (
        <ThemeSelect value={value ?? ""} options={options} onChange={onChange} />
      ) : (
        <span className="field-shell">
          {prefix ? <span className="field-affix pl-3.5">{prefix}</span> : null}
          <input
            className="field-value"
            type="number"
            inputMode="decimal"
            step={field.step || (field.type === "currency" ? "1" : "any")}
            min="0"
            value={value ?? ""}
            onChange={(e) => onChange(e.target.value)}
            aria-label={`${field.label}${unit ? ` in ${unit}` : ""}`}
          />
          {unit ? <span className="field-affix shrink-0 pr-3.5">{unit}</span> : null}
        </span>
      )}
      {field.help ? <span className="mt-1 block text-xs leading-relaxed text-zinc-500">{field.help}</span> : null}
    </div>
  );
}
