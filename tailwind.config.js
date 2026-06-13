/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom healthcare color scheme for rural population - Updated with Almond, Dark Brown, Olive Green
        primary: {
          50: '#EDD5B0',
          100: '#EFDECD',
          600: '#6B8E23',  // Olive Green - Primary
          700: '#556B2F',  // Dark Olive
          800: '#3C4D1F',
        },
        health: {
          600: '#556B2F',  // Olive Green - Wellness, CTAs
          700: '#3C4D1F',
        },
        emergency: {
          600: '#654321',  // Dark Brown - High urgency
          700: '#4A3119',
        },
        warning: {
          500: '#808000',  // Olive Green - Medium urgency
          600: '#6B8E23',
        },
        neutral: {
          50: '#EFDECD',
          100: '#EDD5B0',  // Almond background
          200: '#E8D4A8',
          800: '#654321',  // Dark Brown text
          900: '#3C2817',  // Dark Brown headings
        }
      }
    },
  },
  plugins: [],
  darkMode: 'class',
}

