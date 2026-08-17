/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Manrope", "ui-sans-serif", "system-ui"],
        display: ["Syne", "Manrope", "sans-serif"],
      },
      colors: {
        ink: {
          950: "#070708",
          900: "#0c0c0e",
          850: "#121214",
          800: "#18181b",
          700: "#27272a",
        },
        mist: {
          100: "#f4f4f5",
          300: "#d4d4d8",
          400: "#a1a1aa",
          500: "#71717a",
        },
      },
      boxShadow: {
        glow: "0 0 80px rgba(180,180,190,0.08)",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(14px)" },
          "100%": { opacity: "1", transform: "none" },
        },
        shimmer: {
          "0%": { backgroundPosition: "0% 50%" },
          "100%": { backgroundPosition: "100% 50%" },
        },
        pulseBar: {
          "0%": { transform: "scaleX(0)" },
          "100%": { transform: "scaleX(1)" },
        },
      },
      animation: {
        fadeUp: "fadeUp 0.55s ease both",
        shimmer: "shimmer 6s linear infinite",
      },
    },
  },
  plugins: [],
};
