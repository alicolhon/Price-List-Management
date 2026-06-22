/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bosch: {
          red: '#E20015',
          dark: '#1A1A1A',
          gray: '#5A5A5A',
          light: '#F5F5F5',
        },
      },
    },
  },
  plugins: [],
}

