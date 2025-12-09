/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Outfit", "sans-serif"],
        serif: ["Goudy Bookletter 1911", "serif"],
      },
      keyframes: {
        blob: {
          '4%': { transform: 'translate(0px, 0px) scale(1)' },
          '50%': { transform: 'translate(20px, -10px) scale(1.05)' },
          '100%': { transform: 'translate(0px, 0px) scale(1)' },
        },
        gradientShift: {
          '0%': { 'background-position': '0% 50%' },
          '50%': { 'background-position': '100% 50%' },
          '100%': { 'background-position': '0% 50%' },
        },
      },
      animation: {
        blob: 'blob 8s infinite ease-in-out',
        gradientShift: 'gradientShift 6s ease infinite',
      },
    },
  },
  plugins: [],
}