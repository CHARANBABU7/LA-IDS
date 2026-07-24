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
    },
  },
  plugins: [],
}