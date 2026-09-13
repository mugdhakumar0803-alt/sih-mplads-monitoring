/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: "#1E2761",
        ice: "#CADCFC",
        accent: "#D9A441",
      },
    },
  },
  plugins: [],
}

