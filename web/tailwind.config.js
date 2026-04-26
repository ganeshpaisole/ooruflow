/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: { 500: '#f97316', 600: '#ea580c', 700: '#c2410c' },
      },
    },
  },
  plugins: [],
}
