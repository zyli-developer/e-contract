/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        brand: '#00C28A',
        'brand-dark': '#00a876',
      },
    },
  },
}
