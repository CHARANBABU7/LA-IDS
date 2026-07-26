/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
theme: {
  extend: {
    colors: {
      void: "#0F0D12",
      panel: "#1A1720",
      amber: "#E8A33D",
      rust: "#C1440E",
      slate: "#C9C4D1",
      bone: "#F2EFEA",
    },
    fontFamily: {
      mono: ["'IBM Plex Mono'", "monospace"],
      sans: ["Inter", "sans-serif"],
    },
    keyframes: {
      scanline: {
        "0%": { top: "0%", opacity: "0" },
        "10%": { opacity: "1" },
        "90%": { opacity: "1" },
        "100%": { top: "100%", opacity: "0" },
      },
    },
    animation: {
      scanline: "scanline 0.9s ease-in-out forwards",
    },
  },
},
  plugins: [],
}