/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-poppins)', 'Poppins', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#f5f0fa',
          100: '#e8ddf3',
          200: '#d1bae7',
          300: '#b48fd8',
          400: '#9566c5',
          500: '#7344a8',
          600: '#5c3688',
          700: '#4a316a',
          800: '#3a274f',
          900: '#2a1c3a',
          950: '#1a1025',
        },
        accent: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fdd8a8',
          300: '#fbbe74',
          400: '#f8a63e',
          500: '#f08221',
          600: '#e06b10',
          700: '#b8520f',
          800: '#934214',
          900: '#773814',
        },
        gold: {
          50: '#fdf9ef',
          100: '#f9efd0',
          200: '#f3dfa1',
          300: '#edcf72',
          400: '#e7bf43',
          500: '#d4a82a',
          600: '#aa8622',
          700: '#7f6519',
          800: '#554311',
          900: '#2a2208',
        },
        lavender: {
          50: '#f8f5ff',
          100: '#efe8ff',
          200: '#e0d4ff',
          300: '#c9b3ff',
          400: '#ad89ff',
          500: '#9360ff',
        },
      },
    },
  },
  plugins: [],
};
